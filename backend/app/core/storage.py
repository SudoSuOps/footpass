"""Immutable, atomic filesystem writes for images/reports.

Enforces the storage rules: originals are never overwritten, writes are atomic
(temp file + os.replace), and every write returns a SHA-256 so metadata can
record it. Used by Phase 2 capture; unit-tested now.
"""
from __future__ import annotations

import hashlib
import io
import os
import tempfile
from datetime import date
from pathlib import Path

from PIL import Image


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def original_relpath(user: str, d: date, side: str, view: str, suffix: str = "") -> str:
    """Build the canonical relative path for an original image."""
    stem = f"{side}-{view}{suffix}-original.jpg"
    return f"originals/users/{user}/{d:%Y}/{d:%m}/{d:%Y-%m-%d}/{stem}"


def thumb_relpath(original_rel: str) -> str:
    return original_rel.replace("originals/", "thumbnails/", 1).replace(
        "-original.jpg", "-thumb.jpg"
    )


def make_thumbnail(data: bytes, max_side: int = 320) -> tuple[bytes, int, int]:
    """Return (thumbnail_jpeg_bytes, original_width, original_height)."""
    im = Image.open(io.BytesIO(data))
    im = im.convert("RGB")
    ow, oh = im.size
    im.thumbnail((max_side, max_side))
    out = io.BytesIO()
    im.save(out, format="JPEG", quality=82)
    return out.getvalue(), ow, oh


def atomic_write_bytes(path: str | Path, data: bytes, *, overwrite: bool = False) -> str:
    """Atomically write bytes to path. Refuses to overwrite unless allowed.

    Returns the SHA-256 hex digest of the written data.
    """
    target = Path(path)
    if target.exists() and not overwrite:
        raise FileExistsError("refusing to overwrite an existing file (originals are immutable)")
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(target.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, target)  # atomic on POSIX
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return sha256_bytes(data)
