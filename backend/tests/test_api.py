"""API-level tests: health, system, settings persistence, checks, stubs."""
from __future__ import annotations


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "healthy"
    assert body["database"] == "ok"
    assert "version" in body


def test_system_shape(client):
    r = client.get("/api/system")
    assert r.status_code == 200
    body = r.json()
    for key in ("cpu_count", "memory", "disk", "database", "uptime_seconds"):
        assert key in body
    assert body["disk"]["total_gb"] > 0


def test_settings_persistence(client):
    r = client.patch("/api/settings", json={"setting_key": "display_name", "setting_value": "Sam"})
    assert r.status_code == 200
    rows = client.get("/api/settings").json()
    assert any(s["setting_key"] == "display_name" and s["setting_value"] == "Sam" for s in rows)
    # upsert updates, not duplicates
    client.patch("/api/settings", json={"setting_key": "display_name", "setting_value": "Alex"})
    rows = client.get("/api/settings").json()
    names = [s for s in rows if s["setting_key"] == "display_name"]
    assert len(names) == 1 and names[0]["setting_value"] == "Alex"


def test_check_creation(client):
    r = client.post("/api/checks", json={})
    assert r.status_code == 201
    check = r.json()
    assert check["status"] == "in_progress"
    listed = client.get("/api/checks").json()
    assert any(c["id"] == check["id"] for c in listed)


def test_camera_unavailable(client):
    r = client.get("/api/camera/status")
    assert r.status_code == 200
    assert r.json()["available"] is False


def test_backup_unavailable(client):
    r = client.get("/api/backup/status")
    assert r.status_code == 200
    assert r.json()["available"] is False


def test_export_not_yet(client):
    assert client.post("/api/exports").status_code == 501
    assert client.get("/api/exports").json() == []
