"""SQLAlchemy models for FootPass.

Image binaries are NEVER stored here — only filesystem paths + metadata.
Original images are immutable; processed derivatives get their own rows/paths.
"""
from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    checks: Mapped[list["DailyCheck"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class DailyCheck(Base):
    __tablename__ = "daily_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    check_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="in_progress", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["UserProfile"] = relationship(back_populates="checks")
    images: Mapped[list["FootImage"]] = relationship(
        back_populates="daily_check", cascade="all, delete-orphan"
    )
    observations: Mapped[list["Observation"]] = relationship(
        back_populates="daily_check", cascade="all, delete-orphan"
    )


class FootImage(Base):
    __tablename__ = "foot_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    daily_check_id: Mapped[int] = mapped_column(
        ForeignKey("daily_checks.id", ondelete="CASCADE"), index=True, nullable=False
    )
    side: Mapped[str] = mapped_column(String(10), nullable=False)   # left | right
    view: Mapped[str] = mapped_column(String(20), nullable=False)   # plantar | medial | lateral
    original_path: Mapped[str] = mapped_column(String(512), nullable=False)
    processed_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    thumbnail_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    sha256: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    camera_device: Mapped[str | None] = mapped_column(String(120), nullable=True)
    sharpness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    brightness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_status: Mapped[str] = mapped_column(String(20), default="unknown", nullable=False)
    captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    daily_check: Mapped["DailyCheck"] = relationship(back_populates="images")


class Observation(Base):
    __tablename__ = "observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    daily_check_id: Mapped[int] = mapped_column(
        ForeignKey("daily_checks.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    clinician_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    daily_check: Mapped["DailyCheck"] = relationship(back_populates="observations")


class DeviceSetting(Base):
    __tablename__ = "device_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    setting_key: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    setting_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ExportRecord(Base):
    __tablename__ = "export_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    export_type: Mapped[str] = mapped_column(String(20), nullable=False)  # zip | pdf
    export_path: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


__all__ = [
    "UserProfile",
    "DailyCheck",
    "FootImage",
    "Observation",
    "DeviceSetting",
    "ExportRecord",
]
