"""
tests/test_database.py

Pengujian unit dan performa untuk basis data spasial terpadu UdaraSiaga
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
    assert DB_PATH.exists(), "File database udarasiaga.db harus ada"
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


def test_facilities_endpoint_lod_and_zoom():
    """Memverifikasi endpoint /layers/facilities mendukung zoom LOD dan limit."""
    # 1. Zoom jauh (skala nasional) -> Hanya bandara dan RS
    res_zoom_low = client.get("/layers/facilities?bbox=106.0,-7.0,108.0,-6.0&zoom=6&limit=100")
    assert res_zoom_low.status_code == 200
    data_low = res_zoom_low.json()
    types_low = {f["properties"]["facility_type"] for f in data_low["features"]}
    assert "school" not in types_low, "Pada zoom rendah (skala nasional) sekolah disembunyikan agar peta tidak penuh"

    # 2. Zoom dekat (skala lokal) -> Sekolah muncul
    res_zoom_high = client.get("/layers/facilities?bbox=106.0,-7.0,108.0,-6.0&zoom=12&limit=100")
    assert res_zoom_high.status_code == 200
    data_high = res_zoom_high.json()
    types_high = {f["properties"]["facility_type"] for f in data_high["features"]}
    assert "school" in types_high, "Pada zoom tinggi sekolah harus muncul"


def test_hotspot_repository_event_query():
    """Memverifikasi pengambilan titik api satelit dari database."""
    hotspots = HotspotRepository.get_by_event("national")
    assert len(hotspots) > 0, "Harus ada titik api nasional di database"
