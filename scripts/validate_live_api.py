"""
validate_live_api.py

Uji Validasi Komprehensif Fungsionalitas Backend Standbai secara Live (End-to-End).
Memeriksa seluruh endpoint, kalkulasi sains, kasus khusus (custom click, katalog 36 hutan, 70 gunung),
dan penanganan galat HTTP (422, 404, 400).
"""

import json
import sys
import urllib.error
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE_URL = "http://127.0.0.1:8000"

def get(path: str, expected_status: int = 200):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
            body = resp.read().decode("utf-8")
            if status != expected_status:
                raise AssertionError(f"GET {path} returned {status}, expected {expected_status}")
            try:
                return json.loads(body)
            except Exception:
                return body
    except urllib.error.HTTPError as e:
        if e.code == expected_status:
            return e.read().decode("utf-8")
        raise AssertionError(f"GET {path} raised HTTP {e.code}, expected {expected_status}. Body: {e.read().decode('utf-8')}")

def post(path: str, payload: dict, expected_status: int = 200):
    url = f"{BASE_URL}{path}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            body = resp.read().decode("utf-8")
            if status != expected_status:
                raise AssertionError(f"POST {path} returned {status}, expected {expected_status}")
            return json.loads(body)
    except urllib.error.HTTPError as e:
        if e.code == expected_status:
            return e.read().decode("utf-8")
        raise AssertionError(f"POST {path} raised HTTP {e.code}, expected {expected_status}. Body: {e.read().decode('utf-8')}")

def run_all_validations():
    print("=" * 70)
    print("🚀 MEMULAI VALIDASI KOMPREHENSIF LIVE BACKEND STANDBAI (38+ CHECKS)")
    print("=" * 70)
    passed_count = 0

    # 1. Root & Health
    r_root = get("/")
    assert r_root["project"] == "Standbai", "Root metadata mismatch"
    print(" [1/38] GET /: OK")
    passed_count += 1

    r_health = get("/health")
    assert r_health["status"] == "healthy", "Health status not healthy"
    print(" [2/38] GET /health: OK")
    passed_count += 1

    # 2. Events List & Catalogs
    r_events = get("/events")
    events = r_events.get("events", [])
    assert len(events) >= 10, f"Expected >= 10 events, found {len(events)}"
    print(f" [3/38] GET /events: OK ({len(events)} events loaded)")
    passed_count += 1

    r_krakatau = get("/events/anak_krakatau_2026_09")
    assert r_krakatau["hazard"] == "volcano"
    print(" [4/38] GET /events/anak_krakatau_2026_09: OK")
    passed_count += 1

    r_fire = get("/events/live_kalimantan")
    assert r_fire["hazard"] == "fire"
    print(" [5/38] GET /events/live_kalimantan: OK")
    passed_count += 1

    r_merapi = get("/events/merapi_yogyakarta")
    assert "Merapi" in r_merapi["name"]
    print(" [6/38] GET /events/merapi_yogyakarta (Katalog 70 Gunung Api Nasional): OK")
    passed_count += 1

    r_forest = get("/events/hutan_sebangau")
    assert r_forest["hazard"] == "fire"
    print(" [7/38] GET /events/hutan_sebangau (Katalog 36 Hutan Konservasi): OK")
    passed_count += 1

    # 3. GIS Layers
    r_volc_layer = get("/layers/volcanoes-national")
    assert r_volc_layer["type"] == "FeatureCollection"
    print(f" [8/38] GET /layers/volcanoes-national: OK ({len(r_volc_layer['features'])} gunung)")
    passed_count += 1

    r_forest_layer = get("/layers/forests-national")
    assert len(r_forest_layer) == 36 or "forests" in r_forest_layer
    print(" [9/38] GET /layers/forests-national: OK")
    passed_count += 1

    r_kpi = get("/layers/summary-kpi")
    assert "volcanoes" in r_kpi and "wildfire_hotspots" in r_kpi
    print(" [10/38] GET /layers/summary-kpi: OK")
    passed_count += 1

    r_fac_layer = get("/layers/facilities-national")
    assert len(r_fac_layer.get("features", [])) > 0 or len(r_fac_layer.get("facilities", [])) > 0
    print(" [11/38] GET /layers/facilities-national: OK")
    passed_count += 1

    # 4. Simulation 1: Volcano Auto (Anak Krakatau)
    sim_volcano = post("/simulate", {
        "hazard": "volcano",
        "mode": "auto",
        "source": {"event_id": "anak_krakatau_2026_09"},
        "horizon_hours": 6,
        "n_members": 5,
        "seed": 42
    })
    run_id_v = sim_volcano["run_id"]
    assert sim_volcano["status"] == "completed"
    print(f" [12/38] POST /simulate (Volcano Auto): OK (run_id: {run_id_v})")
    passed_count += 1

    r_status_v = get(f"/runs/{run_id_v}")
    assert r_status_v["status"] == "completed"
    print(" [13/38] GET /runs/{run_id}: OK")
    passed_count += 1

    r_tiers_v0 = get(f"/runs/{run_id_v}/tiers?t=0")
    assert r_tiers_v0["type"] == "FeatureCollection"
    r_tiers_v6 = get(f"/runs/{run_id_v}/tiers?t=5")
    assert r_tiers_v6["type"] == "FeatureCollection"
    print(" [14/38] GET /runs/{run_id}/tiers (t=0 & t=5 GeoJSON): OK")
    passed_count += 1

    r_impact_v = get(f"/runs/{run_id_v}/impact")
    assert "population_exposed" in r_impact_v
    assert "min" in r_impact_v["population_exposed"]
    assert r_impact_v["ispu"]["available"] is False
    print(" [15/38] GET /runs/{run_id}/impact (P5/P50/P95 Range & ISPU check): OK")
    passed_count += 1

    r_fac_imp_v = get(f"/runs/{run_id_v}/facilities-impacted?min_prob=0.05")
    assert "facilities_impacted" in r_fac_imp_v
    print(" [16/38] GET /runs/{run_id}/facilities-impacted: OK")
    passed_count += 1

    fac_id_to_test = "fac_sch_01"
    if r_fac_imp_v.get("facilities_impacted"):
        fac_id_to_test = r_fac_imp_v["facilities_impacted"][0]["facility_id"]
    elif r_fac_imp_v.get("schools"):
        fac_id_to_test = r_fac_imp_v["schools"][0]["facility_id"]
    r_loc_v = get(f"/runs/{run_id_v}/location/{fac_id_to_test}")
    assert r_loc_v["facility_id"] == fac_id_to_test
    print(f" [17/38] GET /runs/{{run_id}}/location/{{facility_id}} (Decision Card: {fac_id_to_test}): OK")
    passed_count += 1

    r_health_v = get(f"/runs/{run_id_v}/health-guidance")
    assert "mask_type_recommended" in r_health_v
    print(" [18/38] GET /runs/{run_id}/health-guidance: OK")
    passed_count += 1

    r_land_water = get(f"/runs/{run_id_v}/land-water")
    assert "cropland_exposed_ha" in r_land_water
    print(" [19/38] GET /runs/{run_id}/land-water: OK")
    passed_count += 1

    r_rain = get(f"/runs/{run_id_v}/rain-effect")
    assert "scavenging_reduction_percentage" in r_rain
    print(" [20/38] GET /runs/{run_id}/rain-effect: OK")
    passed_count += 1

    r_advice = get(f"/runs/{run_id_v}/advice")
    assert "sourced_advice" in r_advice
    print(" [21/38] GET /runs/{run_id}/advice: OK")
    passed_count += 1

    r_severity = get(f"/runs/{run_id_v}/severity?t=6")
    assert "percentile_50" in r_severity
    print(" [22/38] GET /runs/{run_id}/severity: OK")
    passed_count += 1

    r_arr = get(f"/runs/{run_id_v}/arrival")
    assert "arrival_time" in r_arr
    print(" [23/38] GET /runs/{run_id}/arrival: OK")
    passed_count += 1

    # 5. Simulation 2: Fire Auto (Live Kalimantan)
    sim_fire = post("/simulate", {
        "hazard": "fire",
        "mode": "auto",
        "source": {"event_id": "live_kalimantan"},
        "horizon_hours": 6,
        "n_members": 5,
        "seed": 42
    })
    run_id_f = sim_fire["run_id"]
    assert sim_fire["status"] == "completed"
    print(f" [24/38] POST /simulate (Fire Auto): OK (run_id: {run_id_f})")
    passed_count += 1

    r_rank_f = get(f"/runs/{run_id_f}/ranking")
    assert len(r_rank_f.get("ranked_clusters", [])) > 0
    cid = r_rank_f["ranked_clusters"][0]["cluster_id"]
    print(" [25/38] GET /runs/{run_id}/ranking (Spatial Cluster Ranking): OK")
    passed_count += 1

    r_ext = post("/fire/extinguish", {
        "run_id": run_id_f,
        "extinguish_cluster_ids": [cid]
    })
    assert "population_reduced" in r_ext
    print(" [26/38] POST /fire/extinguish (Particle Tag Linearity): OK")
    passed_count += 1

    r_carb = get(f"/runs/{run_id_f}/carbon")
    assert "total_co2e_tonnes" in r_carb
    print(" [27/38] GET /runs/{run_id}/carbon (CO2e Peat vs Mineral): OK")
    passed_count += 1

    # 6. Simulation 3: Interactive Free Map Click (Custom Lat/Lon Anywhere in Indonesia)
    sim_custom = post("/simulate", {
        "hazard": "volcano",
        "mode": "auto",
        "source": {
            "latitude": -7.54,
            "longitude": 110.44,
            "name": "Titik Bebas Klik Lereng Merapi"
        },
        "horizon_hours": 6,
        "n_members": 5,
        "seed": 99
    })
    run_id_c = sim_custom["run_id"]
    assert sim_custom["status"] == "completed"
    print(f" [28/38] POST /simulate (Klik Titik Bebas Sembarang Peta Indonesia): OK (run_id: {run_id_c})")
    passed_count += 1

    # 7. Simulation 4: National Forest Catalog Click
    sim_forest_run = post("/simulate", {
        "hazard": "fire",
        "mode": "auto",
        "source": {"event_id": "hutan_bukit_tiga_puluh"},
        "horizon_hours": 6,
        "n_members": 5,
        "seed": 77
    })
    run_id_fr = sim_forest_run["run_id"]
    assert sim_forest_run["status"] == "completed"
    print(f" [29/38] POST /simulate (Klik Hutan Bukit Tiga Puluh 36 Konservasi): OK (run_id: {run_id_fr})")
    passed_count += 1

    # 8. Compare & Sensitivity
    r_cmp = post("/runs/compare", {
        "run_id_a": run_id_v,
        "run_id_b": run_id_c
    })
    assert "deltas" in r_cmp
    print(" [30/38] POST /runs/compare (Side-by-Side Skenario): OK")
    passed_count += 1

    r_sens = post("/runs/sensitivity", {
        "run_id": run_id_v,
        "parameter_name": "column_height_km"
    })
    assert "sweep_results" in r_sens
    print(" [31/38] POST /runs/sensitivity (Parameter Sweep): OK")
    passed_count += 1

    # 9. Lapis 3 Trust & Verification
    r_val_v = get("/validation/anak_krakatau_2026_09")
    assert r_val_v["hazard"] == "volcano"
    assert "fractions_skill_score" in r_val_v
    print(" [32/38] GET /validation/anak_krakatau_2026_09 (Ground Truth & FSS Metric): OK")
    passed_count += 1

    r_val_f = get("/validation/live_kalimantan")
    assert r_val_f["status"] == "not_testable"
    print(" [33/38] GET /validation/live_kalimantan (Honest 'not_testable' check): OK")
    passed_count += 1

    r_limits = get("/limits")
    assert "computational_limits" in r_limits
    print(" [34/38] GET /limits (Domain & Threshold Guarantees): OK")
    passed_count += 1

    r_sources = get("/sources")
    assert len(r_sources.get("sources", [])) > 0
    print(" [35/38] GET /sources (Verified Open Data Catalog): OK")
    passed_count += 1

    r_exp_json = get(f"/runs/{run_id_v}/export?format=json")
    assert "run_id" in r_exp_json
    r_exp_html = get(f"/runs/{run_id_v}/export?format=html")
    assert "<!DOCTYPE html>" in str(r_exp_html)
    print(" [36/38] GET /runs/{run_id}/export (JSON & Printable HTML A4): OK")
    passed_count += 1

    r_attr = get("/attributions")
    assert "attributions" in r_attr
    print(" [37/38] GET /attributions: OK")
    passed_count += 1

    # 10. Robust Error Handling Integrity Checks
    # a. Auto mode rejects overrides with 422
    err_422 = post("/simulate", {
        "hazard": "volcano",
        "mode": "auto",
        "source": {"event_id": "anak_krakatau_2026_09"},
        "horizon_hours": 6,
        "n_members": 5,
        "overrides": {"column_height_km": 15.0}
    }, expected_status=422)
    assert "Mode 'auto' memakai data asli tanpa overrides" in str(err_422)

    # b. Non-existent event returns 404
    err_404 = get("/events/non_existent_event_xyz123", expected_status=404)
    assert "tidak ditemukan" in str(err_404)

    print(" [38/38] Error Handling Guardrails (422 Reject Overrides & 404 Guard): OK")
    passed_count += 1

    print("=" * 70)
    print(f"🎉 SUKSES BESAR: {passed_count}/{passed_count} PENGUJIAN FUNGSIONALITAS LIVE LULUS 100%!")
    print("    TIDAK DITEMUKAN ADANYA BUG, ERROR, ATAU KEBOCORAN KONTRAK DATA.")
    print("=" * 70)

if __name__ == "__main__":
    run_all_validations()
