#!/usr/bin/env bash

HOST="example.com"
BOT_TOKEN="${BOT_TOKEN:?set BOT_TOKEN}"
CHAT_ID="${CHAT_ID:?set CHAT_ID}"

down=0

while true; do
  if ping -c 1 -W 5 "$HOST" >/dev/null 2>&1; then
    if [ "$down" -eq 1 ]; then
      curl -sS -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
        -d "chat_id=${CHAT_ID}" \
        -d "text=${HOST} is back online on $(hostname) at $(date)"
      down=0
    fi
  else
    if [ "$down" -eq 0 ]; then
      curl -sS -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
        -d "chat_id=${CHAT_ID}" \
        -d "text=Ping failed for ${HOST} on $(hostname) at $(date)"
      down=1
    fi
  fi

  sleep 60
done
