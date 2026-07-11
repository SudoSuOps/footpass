"""Liveness/health + system information endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import get_db
from app.hardware import collect_system_info
from app.schemas import HealthResponse, SystemResponse

router = APIRouter(tags=["health"])


def database_status(db: Session) -> str:
    try:
        db.execute(text("SELECT 1"))
        return "ok"
    except Exception:  # noqa: BLE001 - report, never crash the health check
        return "unavailable"


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)) -> HealthResponse:
    return HealthResponse(
        status="healthy",
        version=settings.footpass_version,
        environment=settings.footpass_env,
        database=database_status(db),
    )


@router.get("/system", response_model=SystemResponse)
def system(db: Session = Depends(get_db)) -> SystemResponse:
    info = collect_system_info(database_status(db))
    return SystemResponse(**info)
