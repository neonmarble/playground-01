#!/usr/bin/env python3
"""Ping monitor with Telegram alerts."""

import argparse
import os
import platform
import subprocess
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime


def ping(host: str) -> bool:
    count, timeout = ("-c", "1", "-W", "3") if platform.system() != "Windows" else ("-n", "1", "-w", "3000")
    cmd = ["ping", *count, host, *timeout]
    return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def send_telegram(bot_token: str, chat_id: str, text: str) -> None:
    params = urllib.parse.urlencode({"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    req = urllib.request.Request(url, data=params.encode())
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"[{datetime.now():%H:%M:%S}] Telegram error: {e}", file=sys.stderr)


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ping monitor with Telegram alerts")
    parser.add_argument("host", nargs="?", default="8.8.8.8", help="Host to monitor (default: 8.8.8.8)")
    parser.add_argument("-i", "--interval", type=int, default=60, help="Check interval in seconds (default: 60)")
    args = parser.parse_args()

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        sys.exit("Error: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set")

    down = False
    print(f"Monitoring {args.host} every {args.interval}s (Ctrl+C to stop)")

    while True:
        if not ping(args.host):
            print(f"[{datetime.now():%H:%M:%S}] {args.host} \u2014 down, sending alert...")
            if not down:
                send_telegram(
                    bot_token,
                    chat_id,
                    f"\U0001f6a8 *Ping Alert*\nHost *{args.host}* is unreachable!\n{timestamp()}",
                )
                down = True
        else:
            print(f"[{datetime.now():%H:%M:%S}] {args.host} \u2014 ok")
            if down:
                send_telegram(
                    bot_token,
                    chat_id,
                    f"\u2705 *Host Recovered*\nHost *{args.host}* is back online!\n{timestamp()}",
                )
                down = False
        time.sleep(args.interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
