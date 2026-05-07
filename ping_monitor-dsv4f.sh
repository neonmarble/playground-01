#!/usr/bin/env bash
set -euo pipefail

HOST="${1:-8.8.8.8}"
BOT_TOKEN="${TELEGRAM_BOT_TOKEN}"
CHAT_ID="${TELEGRAM_CHAT_ID}"
INTERVAL=60

send_alert() {
  local msg="🚨 *Ping Alert*%0AHost *$HOST* is unreachable!%0A$(date '+%Y-%m-%d %H:%M:%S')"
  curl -s --max-time 10 \
    "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
    -d "chat_id=$CHAT_ID&text=$msg&parse_mode=Markdown" > /dev/null
}

echo "🔍 Monitoring $HOST every ${INTERVAL}s (Ctrl+C to stop)"

while true; do
  if ! ping -c 1 -W 3 "$HOST" &> /dev/null; then
    echo "[$(date '+%H:%M:%S')] ✗ $HOST — down, sending alert..."
    send_alert
  else
    echo "[$(date '+%H:%M:%S')] ✓ $HOST — ok"
  fi
  sleep "$INTERVAL"
done
