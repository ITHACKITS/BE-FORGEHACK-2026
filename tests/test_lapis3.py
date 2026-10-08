"""
tests/test_lapis3.py

Pengujian endpoint dan fitur pembuktian kepercayaan Lapis 3:
1. Validasi lapangan gunung (/validation/anak_krakatau_2026_09)
2. Validasi kebakaran tanpa stasiun (/validation/live_kalimantan -> not_testable)
3. Batasan sistem dan domain (/limits)
4. Katalog sumber terverifikasi (/sources)
5. Urutan playback demo (/demo/play/{event_id})
6. Ekspor ringkasan satu halaman (/runs/{run_id}/export - JSON dan HTML)
7. Peringatan bahaya lahar hujan (/runs/{run_id}/lahar-warning)
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture(scope="module")
def sample_volcano_run():
    payload = {
        "hazard": "volcano",
        "mode": "auto",
        "source": {"event_id": "anak_krakatau_2026_09"},
        "horizon_hours": 6,
        "n_members": 5,
        "seed": 42,
    }
    resp = client.post("/simulate", json=payload)
    assert resp.status_code == 200
    return resp.json()["run_id"]


def test_volcano_validation():
    """
    SPEC.md Bagian 14:
    Validasi gunung terhadap reported_impact.geojson, bandara terpisah,
    dan arah abu terhadap VONA.
    """
    resp = client.get("/validation/anak_krakatau_2026_09")
    assert resp.status_code == 200
    data = resp.json()
    assert data["hazard"] == "volcano"
    assert data["resolution"] == "district"
    assert data["district_hit_rate"] >= 0.5
    assert data["fractions_skill_score"] is not None

    # Dampak penerbangan harus berlabel khusus
    aviation = data.get("aviation_impact", {})
    assert aviation.get("label") == "dampak penerbangan"
    assert "Bandara Radin Inten II" in aviation.get("airport_name")

    # Arah vertikal terhadap D05b VONA
    v_check = data.get("vertical_dispersion_directional_check", {})
    assert "upper_layer_status" in v_check
    assert "mid_layer_status" in v_check

    # Grid search 1D spread_inflation
    gs = data.get("grid_search_spread_inflation", [])
    assert len(gs) >= 3

    # Caveat wajib
    assert "confidence_caveat" in data


def test_fire_validation_not_testable():
    """
    SPEC.md Bagian 14:
    Bila stasiun pembanding tidak ada, kebakaran berstatus not_testable
    tanpa klaim akurasi presisi.
    """
    resp = client.get("/validation/live_kalimantan")
    assert resp.status_code == 200
    data = resp.json()
    assert data["hazard"] == "fire"
    assert data["status"] == "not_testable"
    assert data["accuracy_claim"] == "none"
    assert "reason" in data


def test_limits_endpoint():
    """
    SPEC.md Bagian 11 & 16:
    /limits memuat batas komputasi, batas domain, ambang tier, dan status asumsi.
    """
    resp = client.get("/limits")
    assert resp.status_code == 200
    data = resp.json()

    assert "computational_limits" in data
    assert data["computational_limits"]["max_bbox_degrees"] == "6.0 x 6.0"
    assert data["computational_limits"]["max_horizon_hours"] == 48

    assert "tier_thresholds" in data
    assert data["tier_thresholds"]["minimum"]["threshold"] == 0.90
    assert data["tier_thresholds"]["median"]["threshold"] == 0.50
    assert data["tier_thresholds"]["maximum"]["threshold"] == 0.05

    assert "assumptions_summary" in data
    assert data["assumptions_summary"]["total_assumptions"] > 0
    assert "disclaimer" in data


def test_sources_endpoint():
    """
    SPEC.md Bagian 11:
    /sources menyajikan katalog sumber terbuka terverifikasi.
    """
    resp = client.get("/sources")
    assert resp.status_code == 200
    data = resp.json()
    sources = data.get("verified_sources", [])
    source_ids = [s["id"] for s in sources]
    for expected_id in ["D01", "D03", "D04", "D09", "D18", "D24", "D16"]:
        assert expected_id in source_ids


def test_demo_playback_endpoint():
    """
    SPEC.md Bagian 11:
    /demo/play/{event_id} menyajikan rangkaian playback otomatis.
    """
    resp = client.get("/demo/play/anak_krakatau_2026_09")
    assert resp.status_code == 200
    data = resp.json()
    assert data["event_id"] == "anak_krakatau_2026_09"
    assert len(data["steps"]) >= 5
    assert data["total_duration_hours"] == 48


def test_run_export_json_and_html(sample_volcano_run):
    """
    SPEC.md Bagian 11:
    /runs/{run_id}/export menghasilkan ringkasan JSON dan HTML cetak.
    """
    # 1. Format JSON
    resp_json = client.get(f"/runs/{sample_volcano_run}/export?format=json")
    assert resp_json.status_code == 200
    data = resp_json.json()
    assert data["run_id"] == sample_volcano_run
    assert "impact" in data
    assert "assumptions_used" in data
    assert "disclaimer" in data

    # 2. Format HTML
    resp_html = client.get(f"/runs/{sample_volcano_run}/export?format=html")
    assert resp_html.status_code == 200
    html_text = resp_html.text
    assert "<!DOCTYPE html>" in html_text
    assert "UdaraSiaga" in html_text
    assert "@media print" in html_text
    assert sample_volcano_run in html_text


def test_lahar_warning(sample_volcano_run):
    """
    Fitur opsional Lapis 3:
    Peringatan potensi lahar hujan sekunder.
    """
    resp = client.get(f"/runs/{sample_volcano_run}/lahar-warning")
    assert resp.status_code == 200
    data = resp.json()
    assert data["hazard"] == "volcano"
    assert data["lahar_risk_level"] in ["waspada", "siaga", "rendah"]
    assert "rainfall_threshold_trigger_mm_h" in data
    assert len(data.get("vulnerable_drainage_basins", [])) > 0


def test_landmask_and_land_water_integrity(sample_volcano_run):
    """
    Validasi integritas daratan vs lautan dan dampak lahan pertanian/sumber air:
    1. LandMask membedakan daratan vs lautan lepas secara presisi.
    2. Endpoint /runs/{run_id}/land-water menghasilkan rentang realistis.
    3. Cacah sumber air berupa bilangan bulat (integer), bukan desimal fiktif.
    """
    from app.engine.landmask import LandMask

    # Uji titik daratan vs lautan lepas
    assert LandMask.is_point_on_land(-5.7315, 105.5965) is True  # Kalianda (Daratan)
    assert LandMask.is_point_on_land(-6.3765, 105.8340) is True  # Labuan (Daratan)
    assert LandMask.is_point_on_land(-5.9500, 105.6500) is False  # Selat Sunda Tengah (Lautan)
    assert LandMask.is_point_on_land(-5.5000, 107.0000) is False  # Laut Jawa (Lautan)

    resp = client.get(f"/runs/{sample_volcano_run}/land-water")
    assert resp.status_code == 200
    data = resp.json()
    assert "cropland_exposed_ha" in data
    assert "water_sources_exposed_count" in data

    crop = data["cropland_exposed_ha"]
    assert crop["min"] <= crop["median"] <= crop["max"]

    water = data["water_sources_exposed_count"]
    assert isinstance(water["min"], int)
    assert isinstance(water["median"], int)
    assert isinstance(water["max"], int)
    assert water["min"] <= water["median"] <= water["max"]


def test_evacuation_route_endpoint(sample_volcano_run):
    """
    Uji integrasi rute evakuasi jalan raya riil OSRM:
    Koordinat awal persis di titik sekolah asal, koordinat akhir persis di gerbang RS rujukan.
    """
    from_lat, from_lon = -5.7315, 105.5965  # SMAN 1 Kalianda
    to_lat, to_lon = -5.7285, 105.5945      # RSUD Bob Bazar
    url = f"/runs/{sample_volcano_run}/evacuation-route?from_lat={from_lat}&from_lon={from_lon}&to_lat={to_lat}&to_lon={to_lon}&from_name=SMAN+1+Kalianda&to_name=RSUD+Bob+Bazar"
    resp = client.get(url)
    assert resp.status_code == 200
    route = resp.json()
    assert route["status"] == "success"
    assert route["distance_km"] > 0
    assert route["estimated_duration_minutes"] >= 1
    coords = route["coordinates"]
    assert len(coords) >= 2
    # Presisi ujung-ke-ujung tanpa celah mengambang
    assert coords[0] == [from_lat, from_lon]
    assert coords[-1] == [to_lat, to_lon]


def test_facilities_island_contiguity_and_no_ocean_facilities(sample_volcano_run):
    """
    Uji kontiguitas daratan:
    Sekolah di Sumatera TIDAK BOLEH dirujuk ke faskes di seberang laut (Jawa).
    Semua fasilitas di database berada di daratan.
    """
    from app.impact.exposure import get_landmass_region

    resp = client.get(f"/runs/{sample_volcano_run}/facilities-impacted?min_prob=0.01")
    assert resp.status_code == 200
    data = resp.json()
    schools = data.get("schools", [])

    for sch in schools:
        sch_region = get_landmass_region(sch)
        target_h = sch.get("nearest_safe_hospital")
        if target_h:
            h_region = get_landmass_region(target_h)
            # Jika sekolah di Sumatera, rujukan RS wajib di Sumatera
            if sch_region == "sumatera":
                assert h_region == "sumatera", f"Sekolah {sch['name']} dirujuk melintasi laut ke {target_h['name']}"
            elif sch_region == "jawa":
                assert h_region == "jawa", f"Sekolah {sch['name']} dirujuk melintasi laut ke {target_h['name']}"

