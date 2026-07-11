"""Daily checks. Phase 1 supports create/list/get so the dashboard can show
'last completed check'. Capture + completion land in Phase 2/3.
"""
from __future__ import annotations

from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import DailyCheck, UserProfile
from app.schemas import CheckCreate, CheckOut

router = APIRouter(prefix="/checks", tags=["checks"])


def _default_user(db: Session) -> UserProfile:
    user = db.execute(
        select(UserProfile).where(UserProfile.active.is_(True)).order_by(UserProfile.id)
    ).scalars().first()
    if user is None:
        user = UserProfile(display_name="You")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.get("", response_model=list[CheckOut])
def list_checks(db: Session = Depends(get_db)) -> list[DailyCheck]:
    return list(
        db.execute(select(DailyCheck).order_by(DailyCheck.check_date.desc())).scalars()
    )


@router.post("", response_model=CheckOut, status_code=201)
def create_check(payload: CheckCreate, db: Session = Depends(get_db)) -> DailyCheck:
    user = _default_user(db) if payload.user_id is None else db.get(UserProfile, payload.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    check = DailyCheck(
        user_id=user.id,
        check_date=payload.check_date or date.today(),
        started_at=datetime.now(timezone.utc),
        status="in_progress",
    )
    db.add(check)
    db.commit()
    db.refresh(check)
    return check


@router.get("/{check_id}", response_model=CheckOut)
def get_check(check_id: int, db: Session = Depends(get_db)) -> DailyCheck:
    check = db.get(DailyCheck, check_id)
    if check is None:
        raise HTTPException(status_code=404, detail="check not found")
    return check


@router.post("/{check_id}/complete", response_model=CheckOut)
def complete_check(check_id: int, db: Session = Depends(get_db)) -> DailyCheck:
    check = db.get(DailyCheck, check_id)
    if check is None:
        raise HTTPException(status_code=404, detail="check not found")
    check.status = "completed"
    check.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(check)
    return check
