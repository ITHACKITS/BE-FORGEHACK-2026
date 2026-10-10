"""
tests/test_map_modes.py

National map modes: wind field, fire heatmap and smoke paths.
Tests run offline, so the wind comes from data/layers/wind_grid_snapshot.json.
"""

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.services import weather_grid

client = TestClient(app)


def test_wind_to_uv_uses_meteorological_direction():
    # Wind FROM the east blows towards the west: u negative, v zero.
    assert weather_grid._to_uv(10.0, 90.0) == (-10.0, -0.0)
    # Wind FROM the south blows north: v positive.
    assert weather_grid._to_uv(5.0, 180.0) == (-0.0, 5.0)


def test_wind_field_shape_and_labels():
    res = client.get("/layers/wind?hours=72")
    assert res.status_code == 200
    data = res.json()
    assert data["available"] is True
    assert data["origin"] == "snapshot"
    g = data["grid"]
    assert (g["nlat"], g["nlon"]) == (9, 25)
    assert len(data["times"]) == len(data["u"]) == len(data["v"]) >= 1
    assert len(data["times"]) <= 72 // 3 + 1
    assert all(len(row) == g["nlat"] * g["nlon"] for row in data["u"])
    assert data["units"] == "m/s" and data["level"] == "10m"
    assert "stale" in data and data["is_example"] is False


def test_wind_field_upper_level_and_validation():
    assert client.get("/layers/wind?level=850hPa&hours=24").json()["level"] == "850hPa"
    assert client.get("/layers/wind?level=500hPa").status_code == 422
    assert client.get("/layers/wind?hours=999").status_code == 422


def test_wind_window_marks_old_snapshots_stale():
    data = weather_grid.load_snapshot()
    future = datetime(2099, 1, 1, tzinfo=timezone.utc)
    win = weather_grid.window(data, "10m", 24, now=future)
    assert win["stale"] is True
    assert win["times"][0] == data["times"][0]


def test_fire_heatmap_cells():
    res = client.get("/layers/heatmap?kind=fires&days=7")
    assert res.status_code == 200
    data = res.json()
    assert data["available"] is True
    assert data["cells"], "stored hotspots should produce at least one cell"
    assert data["as_of"] >= data["window_start"]
    assert all(c["count"] >= 1 for c in data["cells"])
    assert data["cells"][0]["frp_sum"] == data["max_frp_sum"]


def test_heatmap_validation():
    assert client.get("/layers/heatmap?kind=pm25").status_code == 422
    assert client.get("/layers/heatmap?days=8").status_code == 422


def test_smoke_paths_follow_the_wind_grid():
    res = client.get("/layers/smoke-paths?hours=48")
    assert res.status_code == 200
    data = res.json()
    assert data["available"] is True
    kinds = {p["source_type"] for p in data["paths"]}
    assert kinds == {"fire", "volcano"}
    for p in data["paths"]:
        assert 1 <= len(p["coords"]) <= 49
        assert p["coords"][0] == [round(p["source"]["lat"], 3), round(p["source"]["lon"], 3)]
    assert "not an official warning" in data["note"]
    assert client.get("/layers/smoke-paths?hours=10").status_code == 422
