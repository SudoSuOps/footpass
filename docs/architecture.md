# Architecture

FootPass is a small set of Docker services behind one reverse proxy. Only the
proxy is published to the host; everything else talks over a private Docker
network.

```
              ┌─────────────── ZimaBoard 2 (Docker) ───────────────┐
  browser ──▶ │  footpass-proxy (Caddy :80)                         │
  (phone,     │      /        → footpass-ui   (nginx + static React) │
   tablet,    │      /api/*   → footpass-api  (FastAPI :8000)        │
   laptop)    │      /docs    → footpass-api                         │
              │      /camera/*→ footpass-camera (OpenCV/V4L2 :8001)  │
              │                                                      │
              │  footpass-api ──▶ footpass-db (PostgreSQL, internal) │
              │  footpass-worker (backups/exports)                   │
              │                                                      │
              │  filesystem:  ${FOOTPASS_DATA_DIR}  (images, reports)│
              └──────────────────────────────────────────────────────┘
```

## Principles in the design

- **Local-first / offline.** No service calls the internet. The proxy runs HTTP
  on the LAN; the camera is captured server-side so no browser camera permission
  is needed.
- **Metadata vs. bytes.** PostgreSQL holds only rows (paths, hashes, scores).
  Image bytes live on the filesystem under `${FOOTPASS_DATA_DIR}`.
- **Originals are immutable.** Writes go through `app/core/storage.py`
  (`atomic_write_bytes`, no-overwrite by default) and record a SHA-256.
- **Modular AI.** `worker/app/vision.py` defines `VisionProvider`; v1 uses
  `NoAIProvider` (no model). See [gpu-support.md](gpu-support.md).

## Data flow (per daily check, Phase 2+)

1. UI asks the camera service for a live preview (MJPEG) over `/camera`.
2. User captures → camera returns a frame → API runs quality checks → writes an
   immutable original + thumbnail to the filesystem → records a `FootImage` row.
3. History/compare/export read rows + files; originals are never modified.

## Services & ports

| Service | Image | Internal port | Published |
|---|---|---|---|
| footpass-proxy | caddy:2-alpine | 80 | **80 (host)** |
| footpass-ui | nginx:alpine (built React) | 80 | no |
| footpass-api | python:3.12-slim | 8000 | no (dev: 8000) |
| footpass-camera | python:3.12-slim | 8001 | no |
| footpass-worker | python:3.12-slim | — | no |
| footpass-db | postgres:16-alpine | 5432 | **never** |
