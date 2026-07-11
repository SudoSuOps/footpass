"""Phase 2+ endpoints, present now as honest stubs so the API surface is stable.

Status endpoints return a truthful 'not configured' shape (so the dashboard can
render status cards); action endpoints return 501 until their phase lands.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

router = APIRouter(tags=["preview"])


def _not_yet(feature: str, phase: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"{feature} arrives in {phase}.",
    )


# ---- Camera (real streaming lives in footpass-camera; wired in Phase 2) ----
@router.get("/camera/devices")
def camera_devices() -> dict:
    return {"devices": [], "status": "not_configured", "note": "USB camera wiring lands in Phase 2."}


@router.get("/camera/status")
def camera_status() -> dict:
    return {"available": False, "status": "not_configured"}


@router.post("/camera/capture")
def camera_capture() -> dict:
    raise _not_yet("Camera capture", "Phase 2")


# ---- Images (GET/serve + save are implemented in routers/images.py) ----
@router.patch("/images/{image_id}")
def patch_image(image_id: int) -> dict:
    # Rotate/flip/crop as a *new processed* file lands in Phase 3.
    raise _not_yet("Image editing", "Phase 3")


# ---- Compare ----
@router.get("/compare")
def compare() -> dict:
    raise _not_yet("Image comparison", "Phase 4")


# ---- Exports ----
@router.get("/exports")
def list_exports() -> list:
    return []


@router.post("/exports")
def create_export() -> dict:
    raise _not_yet("Passport export", "Phase 4")


# ---- Backup ----
@router.get("/backup/status")
def backup_status() -> dict:
    return {
        "available": False,
        "status": "not_configured",
        "last_backup": None,
        "note": "NAS backup arrives in Phase 4.",
    }


@router.post("/backup/run")
def backup_run() -> dict:
    raise _not_yet("Backup run", "Phase 4")
