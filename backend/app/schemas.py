"""Pydantic response/request models. Consistent shapes for the API."""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str
    environment: str
    database: str  # "ok" | "unavailable"


class DiskInfo(BaseModel):
    path: str
    total_gb: float
    used_gb: float
    free_gb: float
    percent_used: float


class MemoryInfo(BaseModel):
    total_gb: float
    used_gb: float
    percent_used: float


class GpuInfo(BaseModel):
    name: str
    driver_version: str | None = None
    memory_total_mb: int | None = None
    memory_free_mb: int | None = None
    temperature_c: int | None = None
    power_w: float | None = None


class SystemResponse(BaseModel):
    version: str
    environment: str
    hostname: str
    uptime_seconds: float
    cpu_count: int
    cpu_percent: float
    load_average: list[float]
    memory: MemoryInfo
    disk: DiskInfo
    database: str
    gpu: list[GpuInfo] = Field(default_factory=list)
    cpu_temp_c: float | None = None


class SettingIn(BaseModel):
    setting_key: str
    setting_value: str | None = None


class SettingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    setting_key: str
    setting_value: str | None = None
    updated_at: datetime | None = None


class CheckOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    check_date: date
    status: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    notes: str | None = None


class CheckCreate(BaseModel):
    check_date: date | None = None
    user_id: int | None = None


class ImageIn(BaseModel):
    side: str
    view: str
    image_b64: str
    quality: dict | None = None


class FootImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    daily_check_id: int
    side: str
    view: str
    sha256: str
    width: int
    height: int
    quality_status: str
    sharpness_score: float | None = None
    brightness_score: float | None = None
    captured_at: datetime | None = None
