from __future__ import annotations
import re
from datetime import datetime, timezone
import pytz

VILNIUS_TZ = pytz.timezone("Europe/Vilnius")

def now_vilnius() -> datetime:
    return datetime.now(VILNIUS_TZ)

def to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise ValueError("Datetime must be timezone-aware")
    return dt.astimezone(timezone.utc)

def format_window(start_vilnius: datetime, end_vilnius: datetime) -> str:
    fmt = "%Y-%m-%d %H:%M"
    return f"{start_vilnius.strftime(fmt)}–{end_vilnius.strftime(fmt)} (Europe/Vilnius)"

def slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-{2,}", "-", s).strip("-")

def trim(s: str, n: int = 280) -> str:
    s = s.strip()
    return s if len(s) <= n else s[: max(0, n - 1)].rstrip() + "…"

def public_link(username: str | None, msg_id: int | None) -> str | None:
    if username and msg_id:
        return f"https://t.me/{username}/{msg_id}"
    return None
