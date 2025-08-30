from __future__ import annotations
import os
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION = os.environ["TELEGRAM_SESSION"]
CHANNEL = os.environ.get("TELEGRAM_DELIVERY_CHANNEL")  # '@my_eng_digest' or invite link

def _normalize_target(raw: str) -> str | int:
    s = (raw or "").strip()
    if not s:
        raise RuntimeError("Empty delivery target")
    if s.lstrip("-").isdigit():
        return int(s)
    if s.startswith("http://") or s.startswith("https://"):
        return s
    if not s.startswith("@"):
        s = f"@{s}"
    return s

def send_to_private_channel(markdown_text: str, channel: str | None = None):
    target_raw = channel or CHANNEL
    if not target_raw:
        raise RuntimeError("TELEGRAM_DELIVERY_CHANNEL not set")
    target = _normalize_target(target_raw)
    with TelegramClient(StringSession(SESSION), API_ID, API_HASH) as client:
        client.parse_mode = 'md'
        client.send_message(target, markdown_text)
