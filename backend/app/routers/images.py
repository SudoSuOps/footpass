"""Foot image capture-save + serve.

Save flow: the browser sends the *approved* JPEG (base64). We write an immutable
original (atomic, no-overwrite), a thumbnail, and a FootImage row. Paths are
stored relative to the data dir for portability; serving resolves them safely.
"""
from __future__ import annotations

import base64
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import resolve_under, sanitize_segment
from app.core.storage import (
    atomic_write_bytes,
    make_thumbnail,
    original_relpath,
    thumb_relpath,
)
from app.db import get_db
from app.models import DailyCheck, FootImage
from app.schemas import FootImageOut, ImageIn

router = APIRouter(tags=["images"])

ALLOWED_SIDES = {"left", "right"}
ALLOWED_VIEWS = {"plantar", "medial", "lateral"}
USER = "default"


@router.post("/checks/{check_id}/images", response_model=FootImageOut, status_code=201)
def save_image(check_id: int, payload: ImageIn, db: Session = Depends(get_db)) -> FootImage:
    check = db.get(DailyCheck, check_id)
    if check is None:
        raise HTTPException(status_code=404, detail="check not found")

    side = sanitize_segment(payload.side.lower())
    view = sanitize_segment(payload.view.lower())
    if side not in ALLOWED_SIDES or view not in ALLOWED_VIEWS:
        raise HTTPException(status_code=422, detail="invalid side/view")

    try:
        raw = base64.b64decode(payload.image_b64, validate=True)
    except (ValueError, base64.binascii.Error):
        raise HTTPException(status_code=400, detail="invalid image data") from None
    if len(raw) < 100:
        raise HTTPException(status_code=400, detail="image too small / empty")

    try:
        thumb, width, height = make_thumbnail(raw)
    except Exception:
        raise HTTPException(status_code=400, detail="unreadable image") from None

    data_dir = settings.footpass_data_dir
    ts = datetime.now(timezone.utc)

    # Canonical name first; if an original already exists (immutable), version it.
    orig_rel = original_relpath(USER, check.check_date, side, view)
    if resolve_under(data_dir, orig_rel).exists():
        orig_rel = original_relpath(USER, check.check_date, side, view, suffix=f"-{ts:%H%M%S}")

    orig_full = resolve_under(data_dir, orig_rel)
    sha = atomic_write_bytes(orig_full, raw, overwrite=False)  # never overwrite an original

    thumb_rel = thumb_relpath(orig_rel)
    atomic_write_bytes(resolve_under(data_dir, thumb_rel), thumb, overwrite=True)

    q = payload.quality or {}
    img = FootImage(
        daily_check_id=check.id,
        side=side,
        view=view,
        original_path=orig_rel,
        thumbnail_path=thumb_rel,
        sha256=sha,
        width=width,
        height=height,
        camera_device=str(q.get("device")) if q.get("device") is not None else None,
        sharpness_score=q.get("sharpness"),
        brightness_score=q.get("brightness"),
        quality_status=str(q.get("status", "unknown")),
        captured_at=ts,
    )
    db.add(img)
    db.commit()
    db.refresh(img)
    return img


@router.get("/checks/{check_id}/images", response_model=list[FootImageOut])
def list_check_images(check_id: int, db: Session = Depends(get_db)) -> list[FootImage]:
    return list(
        db.execute(
            select(FootImage).where(FootImage.daily_check_id == check_id).order_by(FootImage.id)
        ).scalars()
    )


def _serve(db: Session, image_id: int, thumb: bool) -> FileResponse:
    img = db.get(FootImage, image_id)
    if img is None:
        raise HTTPException(status_code=404, detail="image not found")
    rel = img.thumbnail_path if thumb else img.original_path
    if not rel:
        raise HTTPException(status_code=404, detail="file not found")
    path = resolve_under(settings.footpass_data_dir, rel)
    if not path.exists():
        raise HTTPException(status_code=404, detail="file missing on disk")
    return FileResponse(path, media_type="image/jpeg")


@router.get("/images/{image_id}")
def get_image(image_id: int, db: Session = Depends(get_db)) -> FileResponse:
    return _serve(db, image_id, thumb=False)


@router.get("/images/{image_id}/thumb")
def get_image_thumb(image_id: int, db: Session = Depends(get_db)) -> FileResponse:
    return _serve(db, image_id, thumb=True)
