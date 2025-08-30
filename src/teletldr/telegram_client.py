from __future__ import annotations
import os
from typing import List, Tuple
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import Channel

def _get_env_int(name: str) -> int:
    v = os.environ.get(name)
    if v is None:
        raise RuntimeError(f"Missing env var: {name}")
    return int(v)

def build_client() -> TelegramClient:
    api_id = _get_env_int("TELEGRAM_API_ID")
    api_hash = os.environ["TELEGRAM_API_HASH"]
    session_str = os.environ["TELEGRAM_SESSION"]
    client = TelegramClient(StringSession(session_str), api_id, api_hash)
    client.connect()
    if not client.is_user_authorized():
        raise RuntimeError("Telethon session not authorized. Re-generate session string.")
    return client

def resolve_engineering_sources(
    client: TelegramClient,
    folder_name: str,
    explicit_channels: List[str]
) -> List[Tuple[Channel, str | None]]:
    """
    Best-effort:
      1) List all dialogs and keep ones whose title contains folder_name (case-insensitive).
      2) Merge with explicit channel usernames/IDs from config.
    Returns list of (Channel, username_or_none)
    """
    folder_name_lower = (folder_name or "").lower()
    dialogs = list(client.iter_dialogs())
    by_folder: List[Tuple[Channel, str | None]] = []

    for d in dialogs:
        title = (d.title or "")
        if folder_name_lower and folder_name_lower in title.lower():
            if isinstance(d.entity, Channel):
                username = getattr(d.entity, "username", None)
                by_folder.append((d.entity, username))

    explicit: List[Tuple[Channel, str | None]] = []
    for ch in explicit_channels or []:
        try:
            entity = client.get_entity(ch)
            if isinstance(entity, Channel):
                username = getattr(entity, "username", None)
                explicit.append((entity, username))
        except Exception:
            pass  # ignore unresolved names

    # Deduplicate by (id, access_hash)
    seen = set()
    result: List[Tuple[Channel, str | None]] = []
    for entity, username in (by_folder + explicit):
        cid = (entity.id, entity.access_hash)
        if cid not in seen:
            seen.add(cid)
            result.append((entity, username))
    return result
