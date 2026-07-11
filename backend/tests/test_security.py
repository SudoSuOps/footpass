"""Path-traversal protection, filename sanitization, PIN hashing."""
from __future__ import annotations

import pytest

from app.core.security import hash_pin, safe_join, sanitize_segment, verify_pin


def test_sanitize_rejects_traversal():
    for bad in ["..", "../etc", "a/b", "foo\x00", "", ".", "/abs"]:
        with pytest.raises(ValueError):
            sanitize_segment(bad)


def test_sanitize_accepts_normal():
    assert sanitize_segment("2026-07-11") == "2026-07-11"
    assert sanitize_segment("right-plantar-original.jpg") == "right-plantar-original.jpg"


def test_safe_join_stays_inside(tmp_path):
    p = safe_join(tmp_path, "users", "default", "photo.jpg")
    assert str(p).startswith(str(tmp_path))


def test_safe_join_blocks_escape(tmp_path):
    with pytest.raises(ValueError):
        safe_join(tmp_path, "..", "..", "etc", "passwd")


def test_pin_hashing():
    h = hash_pin("2468")
    assert h != "2468"
    assert verify_pin("2468", h)
    assert not verify_pin("0000", h)
