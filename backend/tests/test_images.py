"""Capture-save → immutable store → serve, with a synthetic image (no camera)."""
from __future__ import annotations

import base64
import io

from PIL import Image

from app.core.config import settings


def _jpeg(w: int = 320, h: int = 240) -> bytes:
    im = Image.new("RGB", (w, h), (180, 120, 90))
    buf = io.BytesIO()
    im.save(buf, format="JPEG")
    return buf.getvalue()


def test_capture_save_and_serve(client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "footpass_data_dir", str(tmp_path))
    cid = client.post("/api/checks", json={}).json()["id"]
    b64 = base64.b64encode(_jpeg()).decode()

    r = client.post(
        f"/api/checks/{cid}/images",
        json={"side": "right", "view": "plantar", "image_b64": b64,
              "quality": {"brightness": 100, "sharpness": 500, "status": "pass"}},
    )
    assert r.status_code == 201
    img = r.json()
    assert img["width"] == 320 and img["height"] == 240
    assert len(img["sha256"]) == 64

    # immutable original written under the data dir
    assert list((tmp_path / "originals").rglob("*-original.jpg"))
    assert list((tmp_path / "thumbnails").rglob("*-thumb.jpg"))

    listed = client.get(f"/api/checks/{cid}/images").json()
    assert any(i["id"] == img["id"] for i in listed)

    assert client.get(f"/api/images/{img['id']}").status_code == 200
    assert client.get(f"/api/images/{img['id']}/thumb").status_code == 200


def test_reject_bad_side(client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "footpass_data_dir", str(tmp_path))
    cid = client.post("/api/checks", json={}).json()["id"]
    b64 = base64.b64encode(_jpeg()).decode()
    r = client.post(
        f"/api/checks/{cid}/images",
        json={"side": "middle", "view": "plantar", "image_b64": b64},
    )
    assert r.status_code == 422


def test_reject_garbage_image(client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "footpass_data_dir", str(tmp_path))
    cid = client.post("/api/checks", json={}).json()["id"]
    r = client.post(
        f"/api/checks/{cid}/images",
        json={"side": "right", "view": "plantar", "image_b64": base64.b64encode(b"not-an-image").decode()},
    )
    assert r.status_code == 400


def test_complete_check(client):
    cid = client.post("/api/checks", json={}).json()["id"]
    r = client.post(f"/api/checks/{cid}/complete")
    assert r.status_code == 200 and r.json()["status"] == "completed"
