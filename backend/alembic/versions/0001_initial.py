"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-11
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_ts = sa.DateTime(timezone=True)
_now = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("display_name", sa.String(120), nullable=False),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", _ts, server_default=_now, nullable=False),
        sa.Column("updated_at", _ts, server_default=_now, nullable=False),
    )

    op.create_table(
        "daily_checks",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("user_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("check_date", sa.Date, nullable=False),
        sa.Column("started_at", _ts, nullable=True),
        sa.Column("completed_at", _ts, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="in_progress"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", _ts, server_default=_now, nullable=False),
    )
    op.create_index("ix_daily_checks_user_id", "daily_checks", ["user_id"])
    op.create_index("ix_daily_checks_check_date", "daily_checks", ["check_date"])

    op.create_table(
        "foot_images",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "daily_check_id",
            sa.Integer,
            sa.ForeignKey("daily_checks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("side", sa.String(10), nullable=False),
        sa.Column("view", sa.String(20), nullable=False),
        sa.Column("original_path", sa.String(512), nullable=False),
        sa.Column("processed_path", sa.String(512), nullable=True),
        sa.Column("thumbnail_path", sa.String(512), nullable=True),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("width", sa.Integer, nullable=False),
        sa.Column("height", sa.Integer, nullable=False),
        sa.Column("camera_device", sa.String(120), nullable=True),
        sa.Column("sharpness_score", sa.Float, nullable=True),
        sa.Column("brightness_score", sa.Float, nullable=True),
        sa.Column("quality_status", sa.String(20), nullable=False, server_default="unknown"),
        sa.Column("captured_at", _ts, nullable=True),
        sa.Column("created_at", _ts, server_default=_now, nullable=False),
    )
    op.create_index("ix_foot_images_daily_check_id", "foot_images", ["daily_check_id"])
    op.create_index("ix_foot_images_sha256", "foot_images", ["sha256"])

    op.create_table(
        "observations",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "daily_check_id",
            sa.Integer,
            sa.ForeignKey("daily_checks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("user_note", sa.Text, nullable=True),
        sa.Column("clinician_note", sa.Text, nullable=True),
        sa.Column("created_at", _ts, server_default=_now, nullable=False),
        sa.Column("updated_at", _ts, server_default=_now, nullable=False),
    )
    op.create_index("ix_observations_daily_check_id", "observations", ["daily_check_id"])

    op.create_table(
        "device_settings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("setting_key", sa.String(80), nullable=False),
        sa.Column("setting_value", sa.Text, nullable=True),
        sa.Column("updated_at", _ts, server_default=_now, nullable=False),
    )
    op.create_index("ix_device_settings_setting_key", "device_settings", ["setting_key"], unique=True)

    op.create_table(
        "export_records",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("user_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("export_type", sa.String(20), nullable=False),
        sa.Column("export_path", sa.String(512), nullable=False),
        sa.Column("created_at", _ts, server_default=_now, nullable=False),
    )
    op.create_index("ix_export_records_user_id", "export_records", ["user_id"])


def downgrade() -> None:
    op.drop_table("export_records")
    op.drop_table("device_settings")
    op.drop_table("observations")
    op.drop_table("foot_images")
    op.drop_table("daily_checks")
    op.drop_table("user_profiles")
