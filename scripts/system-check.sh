#!/usr/bin/env bash
# One-shot host readiness report for FootPass.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "======================================"
echo "  FootPass system check"
echo "======================================"

echo "-- OS --"
# shellcheck disable=SC1091
. /etc/os-release 2>/dev/null || true
echo "${PRETTY_NAME:-unknown} ($(uname -m))"

echo "-- Docker --"
docker --version 2>/dev/null || echo "docker: NOT INSTALLED"
docker compose version 2>/dev/null || echo "compose plugin: NOT INSTALLED"

echo "-- Disk (data dir) --"
df -h "${FOOTPASS_DATA_DIR:-/srv/footpass}" 2>/dev/null || df -h /

echo "-- Camera --"
bash scripts/detect-camera.sh || true

echo "-- GPU --"
bash scripts/detect-gpu.sh || true

echo "======================================"
echo "  Done."
echo "======================================"
