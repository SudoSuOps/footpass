"""FootPass camera service.

Phase 1: health/status only — proves the service and proxy route work.
Phase 2: USB camera auto-detection (V4L2), MJPEG preview at /camera/preview,
and single-frame capture, all performed ON the ZimaBoard (never the browser).
The camera is attached via docker-compose (devices: /dev/video0) in Phase 2.
"""
from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException, status

VERSION = os.environ.get("FOOTPASS_VERSION", "0.1.0")

app = FastAPI(title="FootPass Camera", version=VERSION, docs_url="/camera/docs")


@app.get("/camera/health")
def health() -> dict:
    return {"status": "healthy", "service": "camera", "version": VERSION}


@app.get("/camera/status")
def camera_status() -> dict:
    # Phase 2 replaces this with real V4L2 enumeration.
    return {"available": False, "status": "not_configured", "devices": []}


@app.get("/camera/preview")
def preview() -> dict:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Live preview (MJPEG) arrives in Phase 2.",
    )
