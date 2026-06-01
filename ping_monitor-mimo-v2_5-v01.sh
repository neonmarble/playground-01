#!/usr/bin/env bash
set -euo pipefail

HOST="${1:-8.8.8.8}"
BOT_TOKEN="${TELEGRAM_BOT_TOKEN}"
CHAT_ID="${TELEGRAM_CHAT_ID}"
INTERVAL=60

down=0

send_alert() {
  local msg="🚨 *Ping Alert*%0AHost *$HOST* is unreachable!%0A$(date '+%Y-%m-%d %H:%M:%S')"
  curl -s --max-time 10 \
    "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
    -d "chat_id=$CHAT_ID&text=$msg&parse_mode=Markdown" > /dev/null
}

send_recovery() {
  local msg="✅ *Host Recovered*%0AHost *$HOST* is back online!%0A$(date '+%Y-%m-%d %H:%M:%S')"
  curl -s --max-time 10 \
    "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
    -d "chat_id=$CHAT_ID&text=$msg&parse_mode=Markdown" > /dev/null
}

echo "Monitoring $HOST every ${INTERVAL}s (Ctrl+C to stop)"

while true; do
  if ! ping -c 1 -W 3 "$HOST" &> /dev/null; then
    echo "[$(date '+%H:%M:%S')] $HOST — down, sending alert..."
    if [ "$down" -eq 0 ]; then
      send_alert
      down=1
    fi
  else
    echo "[$(date '+%H:%M:%S')] $HOST — ok"
    if [ "$down" -eq 1 ]; then
      send_recovery
      down=0
    fi
  fi
  sleep "$INTERVAL"
done
