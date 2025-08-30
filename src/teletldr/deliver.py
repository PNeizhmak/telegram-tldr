from __future__ import annotations
import os
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION = os.environ["TELEGRAM_SESSION"]
CHANNEL = os.environ.get("TELEGRAM_DELIVERY_CHANNEL")  # '@my_eng_digest' or invite link

def send_to_private_channel(markdown_text: str, channel: str | None = None):
    target = channel or CHANNEL
    if not target:
        raise RuntimeError("TELEGRAM_DELIVERY_CHANNEL not set")
    with TelegramClient(StringSession(SESSION), API_ID, API_HASH) as client:
        client.parse_mode = 'md'
        client.send_message(target, markdown_text)
