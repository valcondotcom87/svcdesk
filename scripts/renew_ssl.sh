#!/usr/bin/env bash
set -euo pipefail

DOMAIN="tsm.barokahdigital.cloud"
BACKEND_DIR="/opt/itsm-platform/backend"
CERT_SRC_DIR="/etc/letsencrypt/live/${DOMAIN}"
CERT_DST_DIR="${BACKEND_DIR}/ssl/live/${DOMAIN}"

if ! command -v certbot >/dev/null 2>&1; then
  echo "certbot not found" >&2
  exit 1
fi

sudo certbot renew --quiet

if [ ! -f "${CERT_SRC_DIR}/fullchain.pem" ] || [ ! -f "${CERT_SRC_DIR}/privkey.pem" ]; then
  echo "Certificate files not found at ${CERT_SRC_DIR}" >&2
  exit 1
fi

sudo mkdir -p "${CERT_DST_DIR}"
sudo cp "${CERT_SRC_DIR}/fullchain.pem" "${CERT_DST_DIR}/fullchain.pem"
sudo cp "${CERT_SRC_DIR}/privkey.pem" "${CERT_DST_DIR}/privkey.pem"
sudo chown -R 1000:1000 "${BACKEND_DIR}/ssl"

cd "${BACKEND_DIR}"
docker compose exec nginx nginx -s reload

echo "SSL renewed and Nginx reloaded."
