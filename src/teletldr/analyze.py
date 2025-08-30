from __future__ import annotations
from dataclasses import dataclass
from typing import List
from math import log
from collections import Counter
import re
import yake

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

from .collect import RawMsg
from .utils import now_vilnius

@dataclass
class Highlight:
    msg: RawMsg
    score: float
    summary: str

def _score(m: RawMsg) -> float:
    chars = len((m.text or '').strip())
    has_link = 1.0 if (m.urls) else 0.0
    replies = float(m.replies or 0)
    views = float(m.views or 0)
    fwd = float(m.forwards or 0)
    return 2.0*has_link + 0.6*log(max(2, chars)) + 0.8*replies + 0.3*views + 0.3*fwd

def _summarize(text: str, sentences: int = 2) -> str:
    text = (text or '').strip()
    if not text:
        return ''
    try:
        parser = PlaintextParser.from_string(text, Tokenizer('english'))
        summarizer = TextRankSummarizer()
        sents = summarizer(parser.document, sentences)
        out = ' '.join(str(s) for s in sents).strip()
        return out or text[:280]
    except Exception:
        return text[:280]

def analyze(messages: List[RawMsg], kw_count: int, highlights_count: int):
    if not messages:
        return {'highlights': [], 'keywords': [], 'stats': {'by_channel': {}, 'by_hour': {}, 'top_domains': []}}

    corpus = '\n\n'.join(m.text for m in messages if m.text)
    kw_extractor = yake.KeywordExtractor(top=kw_count, stopwords=None)
    kws = [k for k, _ in kw_extractor.extract_keywords(corpus)]

    scored = [(m, _score(m)) for m in messages]
    scored.sort(key=lambda t: t[1], reverse=True)
    top = scored[:highlights_count]
    highlights = [Highlight(msg=m, score=s, summary=_summarize(m.text, sentences=2)) for (m, s) in top]

    by_channel = Counter(m.channel_title for m in messages)
    by_hour = Counter(m.date_utc.astimezone(now_vilnius().tzinfo).hour for m in messages)

    domain_re = re.compile(r"https?://([^/\s]+)")
    domains = Counter()
    for m in messages:
        for u in m.urls:
            m2 = domain_re.search(u)
            if m2:
                domains[m2.group(1).lower()] += 1
    top_domains = [d for d, _ in domains.most_common(10)]

    return {
        'highlights': highlights,
        'keywords': kws,
        'stats': {'by_channel': dict(by_channel), 'by_hour': dict(sorted(by_hour.items())), 'top_domains': top_domains},
    }
