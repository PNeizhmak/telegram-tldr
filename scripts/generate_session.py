from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import os

api_id = int(os.environ["TELEGRAM_API_ID"])  # from .env
api_hash = os.environ["TELEGRAM_API_HASH"]   # from .env

with TelegramClient(StringSession(), api_id, api_hash) as c:
    print(c.session.save())
