"""
tests/test_lapis2.py

Pengujian endpoint dan fitur pembeda Lapis 2:
1. Peringkat titik api (/runs/{run_id}/ranking)
2. Padamkan titik api (/fire/extinguish)
3. Estimasi gas karbon (/runs/{run_id}/carbon)
4. Dampak lahan dan air abu (/runs/{run_id}/land-water)
5. Efek pencucian hujan (/runs/{run_id}/rain-effect)
6. Komparasi dua skenario (/runs/compare)
7. Analisis sensitivitas parameter (/runs/sensitivity)
8. Rekomendasi saran tindakan (/runs/{run_id}/advice)
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture(scope="module")
def volcano_run():
    payload = {
        "hazard": "volcano",
        "mode": "auto",
        "source": {"event_id": "anak_krakatau_2026_09"},
        "horizon_hours": 6,
        "n_members": 5,
        "seed": 42
    }
    resp = client.post("/simulate", json=payload)
    assert resp.status_code == 200
    return resp.json()["run_id"]


@pytest.fixture(scope="module")
def fire_run():
    payload = {
        "hazard": "fire",
        "mode": "auto",
        "source": {"event_id": "live_kalimantan"},
        "horizon_hours": 6,
        "n_members": 5,
        "seed": 42
    }
    resp = client.post("/simulate", json=payload)
    assert resp.status_code == 200
    return resp.json()["run_id"]


def test_hotspot_ranking(fire_run):
    resp = client.get(f"/runs/{fire_run}/ranking")
    assert resp.status_code == 200
    data = resp.json()
    assert data["hazard"] == "fire"
    clusters = data.get("ranked_clusters", [])
    assert len(clusters) > 0
    # Cek bahwa peringkat terurut dari kontribusi tertinggi
    scores = [c["exposure_contribution_score"] for c in clusters]
    assert scores == sorted(scores, reverse=True)


def test_extinguish_hotspots(fire_run):
    # Ambil peringkat dulu
    rank_resp = client.get(f"/runs/{fire_run}/ranking")
    clusters = rank_resp.json().get("ranked_clusters", [])
    cid_to_extinguish = [clusters[0]["cluster_id"]]

    ext_payload = {
        "run_id": fire_run,
        "extinguish_cluster_ids": cid_to_extinguish
    }
    resp = client.post("/fire/extinguish", json=ext_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "population_reduced" in data
    assert "carbon_reduced_co2e_tonnes" in data
    assert data["reduction_percentage"] > 0.0


def test_carbon_emissions(fire_run):
    resp = client.get(f"/runs/{fire_run}/carbon")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_co2e_tonnes" in data
    assert "peat_emissions_tonnes" in data
    tot = data["total_co2e_tonnes"]
    assert tot["min"] <= tot["median"] <= tot["max"]
    assert "source" in data


def test_land_water_impact(volcano_run):
    resp = client.get(f"/runs/{volcano_run}/land-water")
    assert resp.status_code == 200
    data = resp.json()
    assert "cropland_exposed_ha" in data
    assert "water_sources_exposed_count" in data
    cropland = data["cropland_exposed_ha"]
    assert cropland["min"] <= cropland["median"] <= cropland["max"]
    assert "ash_wetness_warning" in data


def test_rain_effect(volcano_run):
    resp = client.get(f"/runs/{volcano_run}/rain-effect")
    assert resp.status_code == 200
    data = resp.json()
    assert "population_exposure_reduced" in data
    assert "hazard_specific_warning" in data
    pop = data["population_exposure_reduced"]
    assert pop["min"] <= pop["median"] <= pop["max"]


def test_compare_runs(volcano_run):
    # Buat run kedua dengan mode experiment
    exp_payload = {
        "hazard": "volcano",
        "mode": "experiment",
        "source": {"event_id": "anak_krakatau_2026_09"},
        "horizon_hours": 6,
        "n_members": 5,
        "seed": 42,
        "overrides": {"column_height_km": 15.0}
    }
    exp_resp = client.post("/simulate", json=exp_payload)
    run_b_id = exp_resp.json()["run_id"]

    cmp_resp = client.post("/runs/compare", json={"run_id_a": volcano_run, "run_id_b": run_b_id})
    assert cmp_resp.status_code == 200
    data = cmp_resp.json()
    assert "run_a" in data
    assert "run_b" in data
    assert "deltas" in data


def test_parameter_sensitivity(volcano_run):
    payload = {
        "run_id": volcano_run,
        "parameter_name": "column_height_km"
    }
    resp = client.post("/runs/sensitivity", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "sensitivity_curve" in data
    assert len(data["sensitivity_curve"]) > 1


def test_action_advice(volcano_run):
    resp = client.get(f"/runs/{volcano_run}/advice")
    assert resp.status_code == 200
    data = resp.json()
    assert "sourced_advice" in data
    assert any("masker" in adv["action"] for adv in data["sourced_advice"])
    # Saran lain harus available: False
    assert data["additional_guidance"]["available"] is False
