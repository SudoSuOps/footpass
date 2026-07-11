#!/usr/bin/env sh
set -e

echo "[footpass-api] applying database migrations..."
if alembic upgrade head; then
  echo "[footpass-api] migrations applied."
else
  echo "[footpass-api] WARNING: migrations failed; starting anyway so /api/health is reachable."
fi

echo "[footpass-api] starting uvicorn on :8000"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
