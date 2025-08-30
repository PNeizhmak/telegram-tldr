from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Tuple
from telethon.sync import TelegramClient
from telethon.tl.types import Channel
import re

@dataclass
class RawMsg:
    channel_id: int
    channel_title: str
    channel_username: str | None
    msg_id: int
    date_utc: datetime
    text: str
    views: int | None
    forwards: int | None
    replies: int | None
    urls: List[str]

URL_RE = re.compile(r"https?://\S+")

def _extract_urls(text: str) -> List[str]:
    return URL_RE.findall(text or "") if text else []

def collect_recent_24h(
    client: TelegramClient,
    sources: List[Tuple[Channel, str | None]],
    start_utc: datetime,
    min_chars: int,
    max_per_channel: int,
) -> List[RawMsg]:
    assert start_utc.tzinfo is not None
    all_msgs: List[RawMsg] = []

    for entity, username in sources:
        count = 0
        for m in client.iter_messages(entity, limit=None):
            if not m:
                continue
            m_date = m.date.replace(tzinfo=timezone.utc) if m.date.tzinfo is None else m.date.astimezone(timezone.utc)
            if m_date < start_utc:
                break  # messages are newest-first
            text = m.message or ""
            urls = _extract_urls(text)
            if len(text.strip()) < min_chars and not urls:
                continue
            rm = RawMsg(
                channel_id=entity.id,
                channel_title=getattr(entity, "title", "") or "Channel",
                channel_username=username,
                msg_id=m.id,
                date_utc=m_date,
                text=text,
                views=getattr(m, "views", None),
                forwards=getattr(m, "forwards", None),
                replies=(m.replies.replies if getattr(m, "replies", None) else None),
                urls=urls,
            )
            all_msgs.append(rm)
            count += 1
            if count >= max_per_channel:
                break

    return all_msgs
