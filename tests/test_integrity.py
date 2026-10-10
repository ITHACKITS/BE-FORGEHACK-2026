"""
tests/test_integrity.py

Pengujian integritas data dan kepatuhan prinsip AGENTS.md:
1. Mode auto menolak overrides (HTTP 422).
2. Mode experiment selalu membawa scenario_label: "skenario hipotetis".
3. Angka dampak selalu rentang {min, median, max}.
4. Kategori ISPU hanya bila faktor emisi PM2.5 berstatus sourced*.
5. Disclaimer wajib ada di respons.
6. Offline guard memblokir panggilan jaringan saat offline.
7. Endpoint health, events, attributions berfungsi dengan benar.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.offline import OfflineGuardException, assert_online_allowed
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "disclaimer" in data
    assert isinstance(data["offline_mode"], bool)


def test_events_endpoint():
    resp = client.get("/events")
    assert resp.status_code == 200
    events = resp.json().get("events", [])
    event_ids = [e["event_id"] for e in events]
    assert "anak_krakatau_2026_09" in event_ids
    assert "live_kalimantan" in event_ids


def test_attributions_endpoint():
    resp = client.get("/attributions")
    assert resp.status_code == 200
    data = resp.json()
    assert "attributions" in data
    sources = [a["source"] for a in data["attributions"]]
    assert any("WorldPop" in s for s in sources)
    assert any("OpenStreetMap" in s for s in sources)
    assert any("Open-Meteo" in s for s in sources)
    assert any("FIRMS" in s for s in sources)


def test_auto_mode_rejects_overrides_422():
    """
    Prinsip 3 AGENTS.md:
    Mode auto memakai data asli tanpa overrides (HTTP 422 bila ada).
    """
    payload = {
        "hazard": "volcano",
        "mode": "auto",
        "source": {"event_id": "anak_krakatau_2026_09"},
        "horizon_hours": 12,
        "n_members": 5,
        "overrides": {
            "column_height_km": 15.0
        }
    }
    resp = client.post("/simulate", json=payload)
    # Harus ditolak dengan status 422 Unprocessable Entity
    assert resp.status_code == 422
    assert "Mode 'auto' memakai data asli tanpa overrides" in str(resp.json())


def test_experiment_mode_scenario_label():
    """
    Prinsip 3 AGENTS.md:
    Hasil experiment selalu membawa scenario_label: "skenario hipotetis".
    """
    payload = {
        "hazard": "volcano",
        "mode": "experiment",
        "source": {"event_id": "anak_krakatau_2026_09"},
        "horizon_hours": 6,
        "n_members": 5,
        "overrides": {
            "column_height_km": 12.0
        }
    }
    resp = client.post("/simulate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["mode"] == "experiment"
    assert data["scenario_label"] == "skenario hipotetis"
    assert "disclaimer" in data
    assert "assumptions_used" in data


def test_impact_range_and_ispu_status():
    """
    Prinsip 1 & 11 AGENTS.md:
    1. Angka dampak selalu rentang {min, median, max}.
    2. ISPU dinonaktifkan jika faktor emisi PM2.5 masih placeholder.
    """
    # Jalankan simulasi singkat
    payload = {
        "hazard": "volcano",
        "mode": "auto",
        "source": {"event_id": "anak_krakatau_2026_09"},
        "horizon_hours": 6,
        "n_members": 5
    }
    sim_resp = client.post("/simulate", json=payload)
    assert sim_resp.status_code == 200
    run_id = sim_resp.json()["run_id"]

    imp_resp = client.get(f"/runs/{run_id}/impact")
    assert imp_resp.status_code == 200
    imp = imp_resp.json()

    # Periksa struktur rentang {min, median, max}
    for metric_name in ["population_exposed", "children_exposed", "elderly_exposed", "area_exposed_km2"]:
        metric = imp[metric_name]
        assert "min" in metric
        assert "median" in metric
        assert "max" in metric
        assert metric["min"] <= metric["median"] <= metric["max"]

    # Prinsip 11: ISPU harus available: False karena faktor emisi PM2.5 D13b belum sourced*
    assert imp["ispu"]["available"] is False
    assert "reason" in imp["ispu"]


def test_offline_guard(monkeypatch):
    """
    Prinsip 6 AGENTS.md:
    UDARASIAGA_OFFLINE=1 memblokir panggilan jaringan eksternal.
    """
    monkeypatch.setenv("UDARASIAGA_OFFLINE", "1")
    with pytest.raises(OfflineGuardException):
        assert_online_allowed("NASA FIRMS")


def test_forest_boundaries_layer_endpoint():
    """
    Uji endpoint /layers/forest-boundaries:
    Memastikan 36 poligon batas kawasan konservasi resmi termuat secara spasial.
    """
    resp = client.get("/layers/forest-boundaries")
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "FeatureCollection"
    features = data.get("features", [])
    assert len(features) >= 36

    # Periksa poligon TN Sebangau & Tanjung Puting
    sebangau = next((f for f in features if f.get("id") == "hutan_sebangau"), None)
    assert sebangau is not None
    assert sebangau["geometry"]["type"] in ["Polygon", "MultiPolygon"]
    assert sebangau["properties"]["area_ha"] > 100000
    assert "n_hotspots" in sebangau["properties"]


def test_forest_simulation_spatial_boundaries():
    """
    Uji simulasi karhutla dengan batas spasial poligon riil:
    Memastikan simulator menyerap titik api satelit FIRMS riil di dalam batas kawasan.
    """
    payload = {
        "hazard": "fire",
        "mode": "auto",
        "source": {"event_id": "hutan_sebangau"},
        "horizon_hours": 6,
        "n_members": 5,
        "seed": 42,
    }
    resp = client.post("/simulate", json=payload)
    assert resp.status_code == 200
    res = resp.json()
    assert "run_id" in res
    assert res["hazard"] == "fire"
    assert res["status"] == "completed"

    # Periksa poligon asap yang dihasilkan dari titik api spasial
    run_id = res["run_id"]
    t_resp = client.get(f"/runs/{run_id}/tiers?t=0")
    assert t_resp.status_code == 200
    tiers_data = t_resp.json()
    assert tiers_data["type"] == "FeatureCollection"
    assert len(tiers_data["features"]) > 0
