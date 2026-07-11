"""Immutable, atomic filesystem writes for images/reports.

Enforces the storage rules: originals are never overwritten, writes are atomic
(temp file + os.replace), and every write returns a SHA-256 so metadata can
record it. Used by Phase 2 capture; unit-tested now.
"""
from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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
