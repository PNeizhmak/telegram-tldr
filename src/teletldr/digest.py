from __future__ import annotations
import yaml
from datetime import timedelta
from pathlib import Path

from .utils import now_vilnius, to_utc, format_window
from .telegram_client import build_client, resolve_engineering_sources
from .collect import collect_recent_24h
from .analyze import analyze
from .render import render_no_updates, render_full, write_report
from .deliver import send_to_private_channel

def main():
    cfg = yaml.safe_load(Path("config.yaml").read_text(encoding="utf-8"))
    use_folder = (cfg.get("use_folder") or "Engineering")
    explicit_channels = cfg.get("channels") or []
    min_chars = int(cfg.get("min_chars", 120))
    max_per_channel = int(cfg.get("max_per_channel", 200))
    highlights = int(cfg.get("highlights", 10))
    kw_count = int(cfg.get("keywords", 15))

    now_vil = now_vilnius()
    start_vil = now_vil - timedelta(hours=24)
    start_utc = to_utc(start_vil)

    client = build_client()
    sources = resolve_engineering_sources(client, use_folder, explicit_channels)

    msgs = collect_recent_24h(client, sources, start_utc, min_chars, max_per_channel)

    date_str = now_vil.strftime("%Y-%m-%d")
    window_str = format_window(start_vil, now_vil)

    if not msgs:
        md = render_no_updates(date_str, window_str)
    else:
        res = analyze(msgs, kw_count=kw_count, highlights_count=highlights)
        md = render_full(
            date_str=date_str,
            window_str=window_str,
            all_msgs=msgs,
            highlights=res["highlights"],
            keywords=res["keywords"],
            stats=res["stats"],
        )

    out_path = write_report(md, reports_dir="reports", date_str=date_str)

    # Deliver to Telegram private channel
    send_to_private_channel(md)

    # Log a short preview
    print(md.splitlines()[0] if md else "")
    print(md.splitlines()[1] if len(md.splitlines()) > 1 else "")

if __name__ == "__main__":
    main()
