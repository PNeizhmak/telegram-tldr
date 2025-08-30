# telegram-tldr: a daily engineering digest from Telegram

Daily digest of engineering content from your Telegram sources. It reads from a folder named **"Engineering"** (best-effort) and/or an explicit channel list, processes **only the last 24 hours**, and posts a TL;DR to a **private Telegram channel** using your **user session**.

> Disclaimer: This project is not affiliated with Telegram. “Telegram” is a trademark of its respective owners.

## Quick Start

### 1) Create Telegram API credentials
- Go to https://my.telegram.org → API Development Tools → create **API ID** and **API HASH**.

### 2) Generate a session string (locally, once)
> This avoids interactive login in CI. Do **not** commit the string.
```bash
python - <<'PY'
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
api_id = int(input('api_id: '))
api_hash = input('api_hash: ')
with TelegramClient(StringSession(), api_id, api_hash) as c:
    print(c.session.save())
PY
```

Copy the printed **session string**.

### 3) Create a private Telegram channel

* e.g., `Engineering Digest (Personal)`
* Optional: set a username like `@my_eng_digest`

### 4) Add GitHub Secrets (Repo → Settings → Secrets → Actions)

* `TELEGRAM_API_ID` — your API ID
* `TELEGRAM_API_HASH` — your API hash
* `TELEGRAM_SESSION` — the session string from step 2
* `TELEGRAM_DELIVERY_CHANNEL` — `@my_eng_digest` (or your channel link)

### 5) Configure `config.yaml`

* Prefer `use_folder: "Engineering"` (title-based match).
* Add explicit `channels:` as fallback (usernames or IDs).
* Tune filters: `min_chars`, `max_per_channel`, `highlights`, `keywords`.

### 6) Run locally (optional)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export $(grep -v '^#' .env.example | xargs)  # then fill in values
export PYTHONPATH=src
python -m teletldr.digest
```

### 7) Schedule

* GitHub Actions workflow runs daily at **06:25 UTC** (~**09:25 Europe/Vilnius** depending on DST).
* You can also trigger via **Actions → Run workflow**.

## How it works

* Resolves channels by matching dialog titles to `use_folder` and merging with `channels`.
* Pulls messages where `msg.date >= now - 24h`.
* Scores posts (link presence, length, replies, views, forwards).
* Extracts keywords (YAKE) and TL;DRs (TextRank).
* Renders Markdown and **posts to your private Telegram channel** using your user session.

## Configuration (example)

```yaml
use_folder: "Engineering"

channels:
  - "kotlinlang"
  - "python_ru"
  - "tech_news_daily"

min_chars: 120
max_per_channel: 200

highlights: 10
keywords: 15
```

## Troubleshooting

* **No posts delivered**: verify folder name, explicit channels, and that sources are accessible to your account.
* **Delivery error**: ensure `TELEGRAM_DELIVERY_CHANNEL` is correct and your account can post there.
* **Auth issues**: regenerate the session string; store it only in GitHub Secrets.
* **Time window**: job runs in UTC; window is shown in **Europe/Vilnius**.

