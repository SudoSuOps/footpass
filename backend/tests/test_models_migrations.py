"""Model metadata + migration wiring."""
from __future__ import annotations

from datetime import date

from app.db import Base, get_db  # noqa: F401
from app.models import DailyCheck, FootImage, UserProfile

EXPECTED_TABLES = {
    "user_profiles",
    "daily_checks",
    "foot_images",
    "observations",
    "device_settings",
    "export_records",
}


def test_all_tables_registered():
    assert EXPECTED_TABLES.issubset(set(Base.metadata.tables.keys()))


def test_initial_migration_revision():
    # Load the migration by file path (module name starts with a digit).
    import pathlib
    import runpy

    here = pathlib.Path(__file__).resolve().parents[1] / "alembic" / "versions" / "0001_initial.py"
    ns = runpy.run_path(str(here))
    assert ns["revision"] == "0001_initial"
    assert ns["down_revision"] is None


def test_foot_image_metadata_only(tmp_path):
    # FootImage stores paths + metadata, never binary blobs.
    cols = {c.name for c in FootImage.__table__.columns}
    assert {"original_path", "sha256", "width", "height", "quality_status"}.issubset(cols)
    assert not any("blob" in c.name.lower() or "data" == c.name.lower() for c in FootImage.__table__.columns)


def test_daily_check_defaults():
    c = DailyCheck(user_id=1, check_date=date(2026, 7, 11))
    assert c.check_date.year == 2026
