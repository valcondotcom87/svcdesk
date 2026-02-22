#!/usr/bin/env bash
set -euo pipefail

DOMAIN="tsm.barokahdigital.cloud"
REPO_ROOT="/opt/itsm-platform"
BACKEND_DIR="$REPO_ROOT/backend"
FRONTEND_DIR="$REPO_ROOT/fe"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required. Install Docker before running this script." >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required to build the frontend." >&2
  exit 1
fi

if [ ! -f "$BACKEND_DIR/.env" ]; then
  echo "Missing $BACKEND_DIR/.env. Copy .env.production to .env and edit it first." >&2
  exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
  echo "Frontend directory not found at $FRONTEND_DIR" >&2
  exit 1
fi

cd "$FRONTEND_DIR"
cat > .env.production <<EOF
VITE_API_BASE_URL=https://$DOMAIN/api/v1
EOF

npm install
npm run build

rm -rf "$BACKEND_DIR/frontend"
cp -r "$FRONTEND_DIR/dist" "$BACKEND_DIR/frontend"

cd "$BACKEND_DIR"
docker compose up -d --build

# Apply migrations and collect static files
sudo docker compose run --rm backend python manage.py migrate --noinput
sudo docker compose run --rm backend python manage.py collectstatic --noinput

if [ "${CREATE_SUPERUSER:-1}" = "1" ]; then
  sudo docker compose run --rm backend python manage.py createsuperuser
fi

echo "Deploy complete. Visit https://$DOMAIN"
