"""Host hardware/system information for the System Health page.

Runs inside the API container, so it reports what the container can see
(CPU/memory via /proc, disk of the mounted data dir). GPU details are optional
and read from an enrichment file the host writes:  <data_dir>/hardware.json
(produced by scripts/system-check.sh / detect-gpu.sh). This keeps the API free
of any GPU/host dependency while still surfacing the T1000 etc. when available.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import psutil

from app.core.config import settings

_GB = 1024 ** 3


def _disk(path: str) -> dict:
    try:
        usage = psutil.disk_usage(path)
    except OSError:
        usage = psutil.disk_usage("/")
        path = "/"
    return {
        "path": path,
        "total_gb": round(usage.total / _GB, 1),
        "used_gb": round(usage.used / _GB, 1),
        "free_gb": round(usage.free / _GB, 1),
        "percent_used": usage.percent,
    }


def _memory() -> dict:
    vm = psutil.virtual_memory()
    return {
        "total_gb": round(vm.total / _GB, 1),
        "used_gb": round(vm.used / _GB, 1),
        "percent_used": vm.percent,
    }


def _cpu_temp() -> float | None:
    try:
        temps = psutil.sensors_temperatures()
    except (AttributeError, OSError):
        return None
    for key in ("coretemp", "cpu_thermal", "acpitz", "k10temp"):
        if key in temps and temps[key]:
            return round(temps[key][0].current, 1)
    for entries in temps.values():
        if entries:
            return round(entries[0].current, 1)
    return None


def _load_average() -> list[float]:
    try:
        return [round(x, 2) for x in os.getloadavg()]
    except (OSError, AttributeError):
        return [0.0, 0.0, 0.0]


def _gpu_from_enrichment() -> list[dict]:
    """Read optional <data_dir>/hardware.json written by host scripts."""
    candidate = Path(settings.footpass_data_dir) / "hardware.json"
    try:
        data = json.loads(candidate.read_text())
    except (OSError, ValueError):
        return []
    gpus = data.get("gpus", [])
    return gpus if isinstance(gpus, list) else []


def collect_system_info(database_status: str) -> dict:
    return {
        "version": settings.footpass_version,
        "environment": settings.footpass_env,
        "hostname": settings.footpass_hostname,
        "uptime_seconds": round(time.time() - psutil.boot_time(), 0),
        "cpu_count": psutil.cpu_count(logical=True) or 1,
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "load_average": _load_average(),
        "memory": _memory(),
        "disk": _disk(settings.footpass_data_dir),
        "database": database_status,
        "gpu": _gpu_from_enrichment(),
        "cpu_temp_c": _cpu_temp(),
    }
