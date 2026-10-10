"""
app/services/map_modes.py

Data for the two nationwide map modes:
- fire heatmap: FIRMS hotspots aggregated into 0.25° cells;
- smoke paths: forward trajectories from the strongest fire clusters and from
  volcanoes at level II or higher, carried by the national wind grid.

Trajectories use RK2 (midpoint) steps of one hour, the same scheme as the
particle engine, without diffusion: they show where the centre of a plume
drifts, not its width or concentration.
"""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from app.db.repositories.volcano_repo import VolcanoRepository
from app.db.session import get_db_connection
from app.services import weather_grid

CELL_DEG = 0.25
M_PER_DEG_LAT = 110_540.0
M_PER_DEG_LON_EQ = 111_320.0


def _hotspot_rows() -> List[tuple[float, float, float, str]]:
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT latitude, longitude, COALESCE(frp, 0), COALESCE(acq_date, '') FROM hotspots"
        ).fetchall()
        return [(r[0], r[1], float(r[2]), r[3]) for r in rows]
    finally:
        conn.close()


def fire_heatmap(days: int) -> Dict[str, Any]:
    """
    Hotspot counts and summed FRP per 0.25° cell over the `days` ending on the
    latest detection date in the database (`as_of`). The window is anchored on
    the data, not on today, and `as_of` says how old it is.
    """
    rows = [r for r in _hotspot_rows() if r[3]]
    if not rows:
        return {"available": False, "reason": "No hotspot detections are stored.", "cells": []}

    as_of = max(r[3] for r in rows)
    window_start = (date.fromisoformat(as_of) - timedelta(days=days - 1)).isoformat()
    cells: Dict[tuple[int, int], Dict[str, float]] = defaultdict(lambda: {"count": 0, "frp_sum": 0.0})
    for lat, lon, frp, acq in rows:
        if acq < window_start:
            continue
        key = (math.floor(lat / CELL_DEG), math.floor(lon / CELL_DEG))
        cells[key]["count"] += 1
        cells[key]["frp_sum"] += frp

    out = [
        {
            "lat": round((i + 0.5) * CELL_DEG, 3),
            "lon": round((j + 0.5) * CELL_DEG, 3),
            "count": int(c["count"]),
            "frp_sum": round(c["frp_sum"], 1),
        }
        for (i, j), c in cells.items()
    ]
    out.sort(key=lambda c: -c["frp_sum"])
    return {
        "available": True,
        "kind": "fires",
        "cell_deg": CELL_DEG,
        "window_start": window_start,
        "as_of": as_of,
        "source": "NASA FIRMS VIIRS/MODIS NRT detections stored in the StandbAI database",
        "is_example": False,
        "max_count": max((c["count"] for c in out), default=0),
        "max_frp_sum": max((c["frp_sum"] for c in out), default=0.0),
        "cells": out,
    }


def _trace(data: Dict[str, Any], level: str, lat: float, lon: float, hours: int) -> List[List[float]]:
    """Hourly positions [[lat, lon], ...] starting at the source; stops at the grid edge."""
    step_h = data.get("step_hours", weather_grid.STEP_HOURS)
    path = [[round(lat, 3), round(lon, 3)]]
    dt = 3600.0

    def velocity(t_h: float, la: float, lo: float) -> Optional[tuple[float, float]]:
        uv = weather_grid.sample(data, level, t_h / step_h, la, lo)
        if uv is None:
            return None
        u, v = uv
        dlat = v / M_PER_DEG_LAT
        dlon = u / (M_PER_DEG_LON_EQ * max(0.2, math.cos(math.radians(la))))
        return dlat, dlon

    for h in range(hours):
        k1 = velocity(h, lat, lon)
        if k1 is None:
            break
        mid_lat, mid_lon = lat + 0.5 * dt * k1[0], lon + 0.5 * dt * k1[1]
        k2 = velocity(h + 0.5, mid_lat, mid_lon)
        if k2 is None:
            break
        lat, lon = lat + dt * k2[0], lon + dt * k2[1]
        path.append([round(lat, 3), round(lon, 3)])
    return path


def smoke_paths(hours: int, max_fire_sources: int = 15) -> Dict[str, Any]:
    data, origin = weather_grid.get_grid()
    if data is None:
        return {
            "available": False,
            "reason": "Wind grid unavailable: offline mode without a stored snapshot.",
            "paths": [],
        }
    win = weather_grid.window(data, "10m", hours)
    # Slice both levels to the same window so index 0 is "now".
    offset = data["times"].index(win["times"][0])
    sliced = {
        **data,
        "times": data["times"][offset:],
        "levels": {
            lvl: {"u": data["levels"][lvl]["u"][offset:], "v": data["levels"][lvl]["v"][offset:]}
            for lvl in data["levels"]
        },
    }

    heat = fire_heatmap(days=7)
    paths: List[Dict[str, Any]] = []
    for cell in heat.get("cells", [])[:max_fire_sources]:
        paths.append({
            "source_type": "fire",
            "name": f"Fire cluster {cell['lat']:.2f}, {cell['lon']:.2f}",
            "source": {"lat": cell["lat"], "lon": cell["lon"]},
            "frp_sum": cell["frp_sum"],
            "wind_level": "10m",
            "coords": _trace(sliced, "10m", cell["lat"], cell["lon"], hours),
        })
    for v in VolcanoRepository.get_all(level_min=2):
        paths.append({
            "source_type": "volcano",
            "name": v["name"],
            "source": {"lat": v["latitude"], "lon": v["longitude"]},
            "level": v["level"],
            "wind_level": "850hPa",
            "coords": _trace(sliced, "850hPa", v["latitude"], v["longitude"], hours),
        })

    return {
        "available": True,
        "hours": hours,
        "start_time": win["times"][0],
        "marks_every_h": 24,
        "wind_source": data["source"],
        "wind_fetched_at": data["fetched_at"],
        "wind_origin": origin,
        "stale": win["stale"],
        "fires_as_of": heat.get("as_of"),
        "is_example": False,
        "note": (
            "Model estimate, not an official warning. Each line follows the forecast wind from a source "
            "(fire smoke at 10 m, volcanic ash at 850 hPa) and shows where the centre of a plume would drift. "
            "Fire sources are the strongest recent hotspot clusters."
        ),
        "paths": paths,
    }
