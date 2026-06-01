#!/usr/bin/env python3
"""Ping monitor with Telegram alerts."""

import argparse
import json
import logging
import os
import platform
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime


def ping(host: str) -> bool:
    if platform.system() == "Windows":
        cmd = ["ping", "-n", "1", host, "-w", "3000"]
    else:
        cmd = ["ping", "-c", "1", host, "-W", "3"]
    try:
        return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10).returncode == 0
    except subprocess.TimeoutExpired:
        return False


def send_telegram(bot_token: str, chat_id: str, text: str, max_retries: int = 3) -> None:
    params = urllib.parse.urlencode({"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    req = urllib.request.Request(url, data=params.encode())

    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = json.loads(resp.read().decode())
                if not body.get("ok"):
                    logging.error("Telegram API error: %s", body.get("description", "unknown error"))
                    return
            return
        except urllib.error.HTTPError as e:
            if e.code == 429:
                retry_after = int(e.headers.get("Retry-After", 5))
                logging.warning("Rate limited by Telegram, retrying after %ds", retry_after)
                time.sleep(retry_after)
                continue
            logging.error("Telegram HTTP error: %s", e)
            return
        except Exception as e:
            logging.error("Telegram error (attempt %d/%d): %s", attempt + 1, max_retries, e)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    logging.error("Failed to send Telegram message after %d attempts", max_retries)


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ping monitor with Telegram alerts")
    parser.add_argument("host", nargs="?", default="8.8.8.8", help="Host to monitor (default: 8.8.8.8)")
    parser.add_argument("-i", "--interval", type=int, default=60, help="Check interval in seconds (default: 60)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        sys.exit("Error: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set")

    down = False
    backoff = 1
    logging.info("Monitoring %s every %ds (Ctrl+C to stop)", args.host, args.interval)

    try:
        while True:
            if not ping(args.host):
                logging.warning("%s — down", args.host)
                if not down:
                    send_telegram(
                        bot_token, chat_id,
                        f"\U0001f6a8 *Ping Alert*\nHost *{args.host}* is unreachable!\n{timestamp()}",
                    )
                    down = True
                    backoff = 1
            else:
                logging.info("%s — ok", args.host)
                if down:
                    send_telegram(
                        bot_token, chat_id,
                        f"\u2705 *Host Recovered*\nHost *{args.host}* is back online!\n{timestamp()}",
                    )
                    down = False
                    backoff = 1

            if down:
                time.sleep(min(backoff, args.interval))
                backoff = min(backoff * 2, 60)
            else:
                time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
