"""Security helpers: path safety, PIN hashing, security headers.

Path traversal protection is critical — all image/report file access must go
through safe_join so a crafted path can never escape the data directory.
"""
from __future__ import annotations

import re
from pathlib import Path

from passlib.context import CryptContext

# pbkdf2_sha256 is pure-Python (no native bcrypt dependency) and secure for a
# local PIN. Avoids passlib/bcrypt version fragility on the appliance.
_pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Only allow these characters in generated filenames / path segments.
_SAFE_SEGMENT = re.compile(r"^[A-Za-z0-9._-]+$")

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cross-Origin-Opener-Policy": "same-origin",
    # CSP: self only, no external JS/fonts/analytics. 'unsafe-inline' for styles
    # is required by the built CSS; scripts stay strict.
    "Content-Security-Policy": (
        "default-src 'self'; img-src 'self' data: blob:; "
        "style-src 'self' 'unsafe-inline'; script-src 'self'; "
        "connect-src 'self'; font-src 'self'; object-src 'none'; "
        "base-uri 'self'; frame-ancestors 'none'"
    ),
}


def hash_pin(pin: str) -> str:
    return _pwd.hash(pin)


def verify_pin(pin: str, hashed: str) -> bool:
    try:
        return _pwd.verify(pin, hashed)
    except ValueError:
        return False


def sanitize_segment(segment: str) -> str:
    """Return a filesystem-safe single path segment or raise ValueError."""
    segment = segment.strip()
    if not segment or segment in {".", ".."} or not _SAFE_SEGMENT.match(segment):
        raise ValueError("unsafe path segment")
    return segment


def safe_join(base: str | Path, *segments: str) -> Path:
    """Join segments under base, guaranteeing the result stays inside base."""
    base_path = Path(base).resolve()
    target = base_path
    for seg in segments:
        target = target / sanitize_segment(seg)
    resolved = target.resolve()
    if base_path != resolved and base_path not in resolved.parents:
        raise ValueError("path escapes base directory")
    return resolved


def resolve_under(base: str | Path, relpath: str | Path) -> Path:
    """Resolve a stored relative path under base, each segment sanitized."""
    parts = [p for p in Path(relpath).parts if p not in ("", "/", "\\")]
    return safe_join(base, *parts)
