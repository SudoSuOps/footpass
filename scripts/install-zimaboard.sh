#!/usr/bin/env bash
# FootPass installer for Debian/Ubuntu-based systems (ZimaBoard, mini-PCs, NAS).
# Idempotent: safe to re-run.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "============================================"
echo "  FootPass installer"
echo "============================================"

# 1) Docker + Compose
if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: Docker Engine is not installed. Install it first:"
  echo "  https://docs.docker.com/engine/install/"
  exit 1
fi
if ! docker compose version >/dev/null 2>&1; then
  echo "ERROR: Docker Compose plugin not found."
  exit 1
fi
echo "[ok] Docker + Compose present."

# 2) .env (create + auto-generate secrets if still on placeholders)
if [ ! -f .env ]; then
  cp .env.example .env
  echo "[ok] Created .env from template."
fi
if grep -q "change_me" .env; then
  if command -v openssl >/dev/null 2>&1; then
    PW="$(openssl rand -hex 24)"
    SK="$(openssl rand -hex 32)"
    sed -i "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${PW}|" .env
    sed -i "s|^FOOTPASS_SECRET_KEY=.*|FOOTPASS_SECRET_KEY=${SK}|" .env
    echo "[ok] Generated secure POSTGRES_PASSWORD + FOOTPASS_SECRET_KEY."
  else
    echo "[!] openssl not found — edit .env and set POSTGRES_PASSWORD + FOOTPASS_SECRET_KEY."
  fi
fi

# 3) Data directory tree
# shellcheck disable=SC1091
set -a; . ./.env 2>/dev/null || true; set +a
DATA_DIR="${FOOTPASS_DATA_DIR:-/srv/footpass}"
echo "[..] Preparing data dir: ${DATA_DIR}"
sudo mkdir -p "${DATA_DIR}"/{originals,processed,thumbnails,reports,exports,backups,database,models,logs}
sudo chown -R "$(id -u)":"$(id -g)" "${DATA_DIR}" 2>/dev/null || true
echo "[ok] Data directory ready."

# 4) Hardware report (also writes hardware.json for the System Health page)
FOOTPASS_DATA_DIR="${DATA_DIR}" bash scripts/system-check.sh || true

# 5) Build + start
echo "[..] Building and starting the stack (first build can take a few minutes)..."
docker compose up -d --build

# 6) Access info
IP="$(hostname -I | awk '{print $1}')"
echo ""
echo "============================================"
echo "  FootPass is starting."
echo "  Open:  http://${IP}/"
echo ""
echo "  For http://footpass.local, run:"
echo "     sudo bash scripts/configure-hostname.sh"
echo "============================================"
