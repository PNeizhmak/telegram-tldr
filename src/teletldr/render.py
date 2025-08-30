from __future__ import annotations
from pathlib import Path
from typing import List
from .collect import RawMsg
from .analyze import Highlight
from .utils import public_link

def latest_report_path(dir_: str) -> str | None:
    p = Path(dir_)
    if not p.exists():
        return None
    md = sorted(p.glob("*.md"))
    return str(md[-1]) if md else None

def render_no_updates(date_str: str, window_str: str) -> str:
    return f"""# Engineering Digest — {date_str}
Window: {window_str}

No new engineering posts in the last 24h 🚀
"""

def render_full(
    date_str: str,
    window_str: str,
    all_msgs: List[RawMsg],
    highlights: List[Highlight],
    keywords: List[str],
    stats: dict,
) -> str:
    lines = []
    lines.append(f"# Engineering Digest — {date_str}")
    lines.append(f"Window: {window_str}")
    lines.append("")
    lines.append(f"Channels scanned: {len(set(m.channel_id for m in all_msgs))} · Messages: {len(all_msgs)}")
    lines.append("")
    lines.append("## Highlights")
    if not highlights:
        lines.append("_No highlights today._")
    else:
        for h in highlights:
            link = public_link(h.msg.channel_username, h.msg.msg_id)
            title = h.msg.channel_title or "Channel"
            head = f"**{title}**"
            if link:
                head += f" — [source]({link})"
            lines.append(f"- {head}\n  \n  {h.summary}")
    lines.append("\n## Top Links")
    links = []
    for m in all_msgs:
        for u in m.urls:
            links.append((u, m.channel_title))
    if not links:
        lines.append("_No links today._")
    else:
        seen = set()
        for u, ch in links:
            if u in seen:
                continue
            seen.add(u)
            lines.append(f"- [{u}]({u}) — {ch}")
    lines.append("\n## Topics & Keywords")
    lines.append(", ".join(f"`{k}`" for k in keywords) if keywords else "_No keywords extracted._")
    lines.append("\n## Stats")
    if stats:
        bc = stats.get("by_channel", {})
        bh = stats.get("by_hour", {})
        td = stats.get("top_domains", [])
        if bc:
            lines.append("**Messages by channel**")
            for ch, n in sorted(bc.items(), key=lambda t: (-t[1], t[0])):
                lines.append(f"- {ch}: {n}")
        if bh:
            lines.append("\n**Most active hours (Vilnius time)**")
            lines.append(", ".join(f"{h:02d}:00 ({n})" for h, n in bh.items()))
        if td:
            lines.append("\n**Top domains**")
            lines.append(", ".join(td))
    lines.append("\n## Per-Channel Mini TL;DRs")
    by_ch = {}
    for m in all_msgs:
        by_ch.setdefault(m.channel_title, []).append(m)
    for ch, msgs in sorted(by_ch.items(), key=lambda t: t[0].lower()):
        lines.append(f"### {ch}")
        for m in msgs[:5]:
            link = public_link(m.channel_username, m.msg_id)
            first_line = (m.text or "").strip().splitlines()[0] if (m.text or "").strip() else ""
            snippet = first_line[:200]
            if link:
                lines.append(f"- {snippet} — [source]({link})")
            else:
                lines.append(f"- {snippet}")
    return "\n".join(lines)

def write_report(markdown: str, reports_dir: str, date_str: str) -> str:
    p = Path(reports_dir)
    p.mkdir(parents=True, exist_ok=True)
    out = p / f"{date_str}.md"
    out.write_text(markdown, encoding="utf-8")
    return str(out)
