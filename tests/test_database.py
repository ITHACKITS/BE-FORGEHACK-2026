"""
tests/test_database.py

Pengujian unit dan performa untuk basis data spasial terpadu Standbai
(SQLite + R*Tree Spatial Engine + Repository Layer).
"""

import time

from fastapi.testclient import TestClient

from app.db.repositories.facility_repo import FacilityRepository
from app.db.repositories.forest_repo import ForestRepository
from app.db.repositories.hotspot_repo import HotspotRepository
from app.db.repositories.volcano_repo import VolcanoRepository
from app.db.session import DB_PATH, get_db_connection
from app.main import app

client = TestClient(app)


def test_database_tables_and_rtree_exist():
    """Memverifikasi bahwa database dan seluruh tabel virtual R*Tree terpasang sempurna."""
    assert DB_PATH.exists(), "Database file standbai.db must exist"
    conn = get_db_connection()
    try:
        tables = [row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        assert "volcanoes" in tables
        assert "forests" in tables
        assert "facilities" in tables
        assert "hotspots" in tables
        assert "facilities_rtree" in tables
        assert "volcanoes_rtree" in tables
        assert "forests_rtree" in tables
        assert "hotspots_rtree" in tables
    finally:
        conn.close()


def test_volcano_repository_counts():
    """Memverifikasi seluruh 70 gunung api aktif PVMBG tersimpan di database."""
    volcs = VolcanoRepository.get_all()
    assert len(volcs) == 70, f"Harus ada 70 gunung api di database, didapat {len(volcs)}"
    assert VolcanoRepository.count_all() == 70

    # Test get_by_id
    merapi = VolcanoRepository.get_by_id("merapi") or VolcanoRepository.get_by_id("lewotobi_laki_laki")
    assert merapi is not None
    assert "name" in merapi
    assert "elevation_m" in merapi


def test_forest_repository_and_boundaries():
    """Memverifikasi 36 kawasan hutan dan poligon batas riil tersedia di database."""
    forests = ForestRepository.get_all()
    assert len(forests) >= 36, f"Harus ada minimal 36 hutan di database, didapat {len(forests)}"

    boundaries = ForestRepository.get_all_boundaries_geojson()
    assert boundaries["type"] == "FeatureCollection"
    assert len(boundaries["features"]) > 0


def test_facility_repository_spatial_bbox_latency():
    """
    Memverifikasi kueri spasial R*Tree BBOX pada ribuan fasilitas
    berjalan sangat cepat (di bawah 20 milidetik).
    """
    # Warmup connection
    FacilityRepository.get_by_bbox(lat_min=-7.0, lat_max=-6.5, lon_min=106.0, lon_max=107.0, limit=10)

    t0 = time.perf_counter()
    # BBOX sekitar Jawa Barat & Banten
    results = FacilityRepository.get_by_bbox(
        lat_min=-7.5,
        lat_max=-6.0,
        lon_min=105.0,
        lon_max=108.5,
        limit=100
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000

    assert len(results) > 0, "Harus menemukan fasilitas di BBOX Jawa Barat/Banten"
    assert elapsed_ms < 50.0, f"Kueri R*Tree spasial harus < 50 ms, didapat {elapsed_ms:.2f} ms"


def test_facilities_endpoint_serves_airports_only():
    """Schools and healthcare stay in SQLite but the API only serves airports (2026-10-10)."""
    for zoom in (6, 12):
        res = client.get(f"/layers/facilities?bbox=105.0,-7.5,108.5,-6.0&zoom={zoom}&limit=500")
        assert res.status_code == 200
        types = {f["properties"]["facility_type"] for f in res.json()["features"]}
        assert types <= {"airport"}, f"zoom {zoom} returned {types}"

    res_school = client.get("/layers/facilities?bbox=95.0,-11.0,141.0,6.0&facility_type=school&limit=500")
    assert res_school.status_code == 200
    assert res_school.json()["features"] == []

    assert FacilityRepository.count_all() == FacilityRepository.count_all("airport") > 0
    assert FacilityRepository.count_all("school") == 0


def test_hotspot_repository_event_query():
    """Memverifikasi pengambilan titik api satelit dari database."""
    hotspots = HotspotRepository.get_by_event("national")
    assert len(hotspots) > 0, "Harus ada titik api nasional di database"
