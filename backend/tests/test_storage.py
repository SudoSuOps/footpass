"""Storage rules: original immutability, atomic writes, duplicate prevention,
checksum determinism (backup-verify stand-in)."""
from __future__ import annotations

import pytest

from app.core.storage import atomic_write_bytes, sha256_bytes


def test_atomic_write_and_hash(tmp_path):
    p = tmp_path / "originals" / "right-plantar-original.jpg"
    digest = atomic_write_bytes(p, b"fake-jpeg-bytes")
    assert p.exists()
    assert digest == sha256_bytes(b"fake-jpeg-bytes")


def test_original_is_immutable(tmp_path):
    p = tmp_path / "right-plantar-original.jpg"
    atomic_write_bytes(p, b"first")
    with pytest.raises(FileExistsError):
        atomic_write_bytes(p, b"second")  # must not overwrite an original
    assert p.read_bytes() == b"first"


def test_overwrite_allowed_when_explicit(tmp_path):
    p = tmp_path / "processed.jpg"
    atomic_write_bytes(p, b"a")
    atomic_write_bytes(p, b"b", overwrite=True)
    assert p.read_bytes() == b"b"


def test_checksum_is_deterministic():
    assert sha256_bytes(b"same") == sha256_bytes(b"same")
    assert sha256_bytes(b"a") != sha256_bytes(b"b")
