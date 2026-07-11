"""Vision review via a local-network MedGemma node (Ollama).

Fails OPEN: if the AI node is unreachable or disabled, the review simply isn't
available — FootPass keeps working. Output is strictly observational; the prompt
forbids diagnosis (see docs/security.md + the wellness-language rules).
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

from app.core.config import settings

# Calm, non-diagnostic. Freddy organizes and describes; he never diagnoses.
REVIEW_PROMPT = (
    "You are Freddy, a calm, friendly assistant that helps a person organize photographs "
    "of their own feet over time. You are NOT a doctor. You must NOT diagnose, name any "
    "medical condition, or give medical advice. Look at the photo(s) and, in 2 to 4 short "
    "plain sentences, describe ONLY what is visually observable — for example skin tone, "
    "dryness, an area of redness, or a visible difference between photos if more than one "
    "is shown. Use everyday words. Do not mention any specific disease or treatment. "
    "Finish with one gentle sentence reminding the person to contact their clinician if "
    "they notice a new or concerning change."
)


class VisionUnavailable(Exception):
    """Raised when AI review can't run (disabled or node unreachable)."""


def _post(path: str, payload: dict, timeout: int) -> dict:
    url = settings.footpass_vision_endpoint.rstrip("/") + path
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def vision_status() -> dict:
    base = {
        "provider": settings.footpass_vision_provider,
        "endpoint": settings.footpass_vision_endpoint,
        "model": settings.footpass_vision_model,
    }
    if settings.footpass_vision_provider == "none":
        return {**base, "enabled": False, "reachable": False}
    try:
        url = settings.footpass_vision_endpoint.rstrip("/") + "/api/version"
        with urllib.request.urlopen(url, timeout=5) as resp:
            ver = json.load(resp).get("version")
        return {**base, "enabled": True, "reachable": True, "version": ver}
    except (urllib.error.URLError, OSError, ValueError):
        return {**base, "enabled": True, "reachable": False}


def review_images(images_b64: list[str], context_note: str = "") -> str:
    """Send images to the MedGemma node and return an observational review."""
    if settings.footpass_vision_provider == "none":
        raise VisionUnavailable("AI review is disabled (FOOTPASS_VISION_PROVIDER=none).")
    if not images_b64:
        raise VisionUnavailable("no images to review")

    prompt = REVIEW_PROMPT + (f"\n\nContext: {context_note}" if context_note else "")
    payload = {
        "model": settings.footpass_vision_model,
        "prompt": prompt,
        "images": images_b64,
        "stream": False,
    }
    try:
        data = _post("/api/generate", payload, settings.footpass_vision_timeout)
    except (urllib.error.URLError, OSError) as e:
        raise VisionUnavailable(f"MedGemma node unreachable: {e}") from None
    except ValueError as e:
        raise VisionUnavailable(f"bad response from MedGemma node: {e}") from None

    text = (data.get("response") or "").strip()
    if not text:
        raise VisionUnavailable(data.get("error") or "empty response from MedGemma node")
    return text
