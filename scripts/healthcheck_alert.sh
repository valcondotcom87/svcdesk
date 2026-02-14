#!/usr/bin/env bash
set -euo pipefail

BACKEND_DIR="/opt/itsm-platform/backend"
ALERT_EMAIL_TO="${ALERT_EMAIL_TO:-}"
ALERT_EMAIL_FROM="${ALERT_EMAIL_FROM:-itsm-alerts@localhost}"
ALERT_EMAIL_SUBJECT="${ALERT_EMAIL_SUBJECT:-[ITSM] Container Health Alert}"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"

cd "$BACKEND_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker not found" >&2
  exit 1
fi

mapfile -t UNHEALTHY < <(docker compose ps --format json | \
  python3 - <<'PY'
import json, sys
items = [json.loads(line) for line in sys.stdin if line.strip()]
for it in items:
    status = (it.get('Health') or it.get('State') or '').lower()
    name = it.get('Name') or it.get('Service') or ''
    if 'unhealthy' in status or status.startswith('restarting'):
        print(f"{name} :: {it.get('State','')} :: {it.get('Health','')}")
PY
)

if [ ${#UNHEALTHY[@]} -eq 0 ]; then
  exit 0
fi

MESSAGE="Unhealthy or restarting containers detected on $(hostname):\n\n$(printf '%s\n' "${UNHEALTHY[@]}")"

if [ -n "$ALERT_EMAIL_TO" ]; then
  if command -v sendmail >/dev/null 2>&1; then
    {
      echo "From: ${ALERT_EMAIL_FROM}"
      echo "To: ${ALERT_EMAIL_TO}"
      echo "Subject: ${ALERT_EMAIL_SUBJECT}"
      echo
      echo -e "$MESSAGE"
    } | sendmail -t
  else
    echo "sendmail not available; cannot send email" >&2
  fi
fi

if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
  curl -sS -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" \
    --data-urlencode "text=${MESSAGE}" >/dev/null || true
fi

exit 0
