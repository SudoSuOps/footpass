"""Device settings — simple key/value store backed by DeviceSetting."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import DeviceSetting
from app.schemas import SettingIn, SettingOut

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=list[SettingOut])
def list_settings(db: Session = Depends(get_db)) -> list[DeviceSetting]:
    return list(db.execute(select(DeviceSetting)).scalars())


@router.patch("", response_model=SettingOut)
def upsert_setting(payload: SettingIn, db: Session = Depends(get_db)) -> DeviceSetting:
    row = db.execute(
        select(DeviceSetting).where(DeviceSetting.setting_key == payload.setting_key)
    ).scalar_one_or_none()
    if row is None:
        row = DeviceSetting(setting_key=payload.setting_key, setting_value=payload.setting_value)
        db.add(row)
    else:
        row.setting_value = payload.setting_value
    db.commit()
    db.refresh(row)
    return row
