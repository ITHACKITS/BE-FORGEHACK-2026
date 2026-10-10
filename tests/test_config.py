"""
tests/test_config.py

BE-02 configuration: offline flag, CORS allow-list and English API metadata.
"""

from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.offline import is_offline
from app.main import app

client = TestClient(app)


def test_offline_defaults_to_online(monkeypatch):
    monkeypatch.delenv("STANDBAI_OFFLINE", raising=False)
    monkeypatch.delenv("UDARASIAGA_OFFLINE", raising=False)
    assert is_offline() is False


def test_offline_legacy_fallback(monkeypatch):
    monkeypatch.delenv("STANDBAI_OFFLINE", raising=False)
    monkeypatch.setenv("UDARASIAGA_OFFLINE", "1")
    assert is_offline() is True


def test_offline_new_flag_wins_over_legacy(monkeypatch):
    monkeypatch.setenv("STANDBAI_OFFLINE", "0")
    monkeypatch.setenv("UDARASIAGA_OFFLINE", "1")
    assert is_offline() is False


def test_cors_allows_listed_origin():
    origin = settings.CORS_ORIGINS[0]
    resp = client.get("/health", headers={"Origin": origin})
    assert resp.headers.get("access-control-allow-origin") == origin


def test_cors_rejects_unlisted_origin():
    resp = client.get("/health", headers={"Origin": "https://unlisted.example"})
    assert "access-control-allow-origin" not in resp.headers


def test_root_uses_new_name_and_disclaimer():
    data = client.get("/").json()
    assert data["project"] == "Standbai"
    assert "Not an official warning" in data["disclaimer"]


def test_openapi_tags_are_english():
    tags = {tag for op in client.get("/openapi.json").json()["paths"].values() for m in op.values() for tag in m.get("tags", [])}
    assert tags == {"health", "events", "simulation", "analysis", "trust", "layers", "attributions"}
