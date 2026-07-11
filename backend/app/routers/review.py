"""On-demand AI review ("Ask Freddy to look") via the MedGemma node.

v1: reviews a single daily check's photos. Observational only, not persisted to
the medical record (kept as a live, optional lens over the owned photos).
"""
from __future__ import annotations

import base64

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import resolve_under
from app.db import get_db
from app.models import DailyCheck, FootImage
from app.vision import VisionUnavailable, review_images, vision_status

router = APIRouter(tags=["review"])

# One image per review: the 8GB Orin runs single-image vision reliably; multiple
# images at once exceed its memory. Multi-image comparison awaits a smaller quant.
MAX_IMAGES = 1


@router.get("/vision/status")
def status() -> dict:
    return vision_status()


@router.post("/checks/{check_id}/review")
def review_check(check_id: int, db: Session = Depends(get_db)) -> dict:
    check = db.get(DailyCheck, check_id)
    if check is None:
        raise HTTPException(status_code=404, detail="check not found")

    images = list(
        db.execute(
            select(FootImage).where(FootImage.daily_check_id == check_id).order_by(FootImage.id)
        ).scalars()
    )
    if not images:
        raise HTTPException(status_code=400, detail="this check has no photos to review")

    b64: list[str] = []
    labels: list[str] = []
    for img in images[:MAX_IMAGES]:
        try:
            path = resolve_under(settings.footpass_data_dir, img.original_path)
            b64.append(base64.b64encode(path.read_bytes()).decode())
            labels.append(f"{img.side} {img.view}")
        except (OSError, ValueError):
            continue
    if not b64:
        raise HTTPException(status_code=400, detail="could not read photos for this check")

    context = f"Photos in this check: {', '.join(labels)}. Date: {check.check_date}."
    try:
        text = review_images(b64, context_note=context)
    except VisionUnavailable as e:
        # Fail open — the review is optional; FootPass keeps working.
        raise HTTPException(status_code=503, detail=str(e)) from None

    return {
        "check_id": check_id,
        "images_reviewed": len(b64),
        "views": labels,
        "model": settings.footpass_vision_model,
        "review": text,
        "disclaimer": (
            "FootPass helps you organize and compare images. It does not diagnose "
            "medical conditions. Contact your clinician if you notice a new or "
            "concerning change."
        ),
    }
