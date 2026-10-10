"""
app/services/weather_grid.py

National wind grid for the map's "wind & smoke" mode.

Open-Meteo forecast API, multi-location requests over Indonesia on a 2° grid
(25 × 9 = 225 points), hourly 10 m and 850 hPa wind for 16 days, resampled to
3-hourly u/v components in m/s.
- Cached in memory for 3 hours.
- A snapshot on disk (data/layers/wind_grid_snapshot.json) serves offline mode
  (STANDBAI_OFFLINE=1) and upstream failures; responses then say `stale`.
- Outbound calls go only to the fixed Open-Meteo host below.
"""

from __future__ import annotations

import json
import math
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import DATA_DIR
from app.core.offline import is_offline

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
SOURCE = "Open-Meteo forecast API (best_match model blend)"

# west, south, east, north
BBOX = (94.0, -11.0, 142.0, 6.0)
STEP_DEG = 2.0
FORECAST_DAYS = 16
STEP_HOURS = 3
LEVELS = ("10m", "850hPa")
CHUNK = 75  # grid points per request, keeps URLs and responses small
TIMEOUT_S = 20.0
CACHE_TTL_S = 3 * 3600
STALE_AFTER_S = 6 * 3600

SNAPSHOT_FILE = DATA_DIR / "layers" / "wind_grid_snapshot.json"

_lock = threading.Lock()
_cache: Dict[str, Any] = {"data": None, "loaded_at": 0.0}


def grid_spec() -> Dict[str, Any]:
    west, south, east, north = BBOX
    nlon = int(round((east - west) / STEP_DEG)) + 1
    nlat = int(math.floor((north - south) / STEP_DEG)) + 1
    return {"lat0": south, "lon0": west, "dlat": STEP_DEG, "dlon": STEP_DEG, "nlat": nlat, "nlon": nlon}


def grid_points() -> List[tuple[float, float]]:
    """Row-major (lat, lon) points: index = i_lat * nlon + i_lon."""
    g = grid_spec()
    return [
        (g["lat0"] + i * g["dlat"], g["lon0"] + j * g["dlon"])
        for i in range(g["nlat"])
        for j in range(g["nlon"])
    ]


def _to_uv(speed: Optional[float], direction_from_deg: Optional[float]) -> tuple[float, float]:
    """Meteorological direction (where the wind comes FROM) to u (east) / v (north)."""
    if speed is None or direction_from_deg is None:
        return 0.0, 0.0
    rad = math.radians(direction_from_deg)
    return round(-speed * math.sin(rad), 1), round(-speed * math.cos(rad), 1)


def fetch_grid() -> Dict[str, Any]:
    """Download the full grid from Open-Meteo. Raises on network or format errors."""
    points = grid_points()
    hourly_vars = ",".join(
        f"wind_speed_{lvl},wind_direction_{lvl}" for lvl in LEVELS
    )
    per_point: List[Dict[str, Any]] = []
    with httpx.Client(timeout=TIMEOUT_S) as client:
        for start in range(0, len(points), CHUNK):
            chunk = points[start:start + CHUNK]
            params = {
                "latitude": ",".join(f"{lat:.2f}" for lat, _ in chunk),
                "longitude": ",".join(f"{lon:.2f}" for _, lon in chunk),
                "hourly": hourly_vars,
                "forecast_days": FORECAST_DAYS,
                "wind_speed_unit": "ms",
                "timezone": "GMT",
            }
            resp = client.get(FORECAST_URL, params=params)
            resp.raise_for_status()
            body = resp.json()
            items = body if isinstance(body, list) else [body]
            if len(items) != len(chunk):
                raise ValueError(f"Open-Meteo returned {len(items)} locations for {len(chunk)} requested")
            per_point.extend(items)

    hourly_times = per_point[0]["hourly"]["time"]
    step_idx = list(range(0, len(hourly_times), STEP_HOURS))
    times = [hourly_times[k] + "Z" for k in step_idx]

    levels: Dict[str, Dict[str, List[List[float]]]] = {}
    for lvl in LEVELS:
        u_t: List[List[float]] = []
        v_t: List[List[float]] = []
        for k in step_idx:
            u_row, v_row = [], []
            for item in per_point:
                h = item["hourly"]
                u, v = _to_uv(h[f"wind_speed_{lvl}"][k], h[f"wind_direction_{lvl}"][k])
                u_row.append(u)
                v_row.append(v)
            u_t.append(u_row)
            v_t.append(v_row)
        levels[lvl] = {"u": u_t, "v": v_t}

    return {
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": SOURCE,
        "grid": grid_spec(),
        "step_hours": STEP_HOURS,
        "times": times,
        "levels": levels,
    }


def save_snapshot(data: Dict[str, Any]) -> None:
    SNAPSHOT_FILE.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_FILE.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")


def load_snapshot() -> Optional[Dict[str, Any]]:
    if not SNAPSHOT_FILE.exists():
        return None
    return json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))


def get_grid() -> tuple[Optional[Dict[str, Any]], str]:
    """
    Return (grid data, origin) where origin is "live", "cache" or "snapshot".
    Data is None only when offline (or the upstream failed) and no snapshot exists.
    """
    with _lock:
        now = time.time()
        if _cache["data"] is not None and now - _cache["loaded_at"] < CACHE_TTL_S:
            return _cache["data"], "cache"
        if not is_offline():
            try:
                data = fetch_grid()
                _cache.update(data=data, loaded_at=now)
                return data, "live"
            except (httpx.HTTPError, ValueError, KeyError, IndexError):
                pass  # fall through to the snapshot
        snap = load_snapshot()
        return snap, "snapshot"


def _parse(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)


def window(data: Dict[str, Any], level: str, hours: int, now: Optional[datetime] = None) -> Dict[str, Any]:
    """Slice the grid to [now, now + hours]. Old snapshots start at their first step."""
    now = now or datetime.now(timezone.utc)
    times = data["times"]
    start = next(
        (i for i, t in enumerate(times) if _parse(t) >= now - timedelta(hours=STEP_HOURS / 2)),
        None,
    )
    out_of_range = start is None
    if start is None:
        start = 0
    n_steps = hours // STEP_HOURS + 1
    end = min(len(times), start + n_steps)
    lvl = data["levels"][level]
    fetched = _parse(data["fetched_at"][:16] + "Z")
    return {
        "times": times[start:end],
        "u": lvl["u"][start:end],
        "v": lvl["v"][start:end],
        "stale": out_of_range or (now - fetched).total_seconds() > STALE_AFTER_S,
    }


def sample(data: Dict[str, Any], level: str, t_index: float, lat: float, lon: float) -> Optional[tuple[float, float]]:
    """Bilinear in space, linear in time. Returns (u, v) or None outside the grid."""
    g = data["grid"]
    fi = (lat - g["lat0"]) / g["dlat"]
    fj = (lon - g["lon0"]) / g["dlon"]
    if not (0 <= fi <= g["nlat"] - 1 and 0 <= fj <= g["nlon"] - 1):
        return None
    lvl = data["levels"][level]
    n_t = len(lvl["u"])
    t0 = max(0, min(n_t - 1, int(math.floor(t_index))))
    t1 = min(n_t - 1, t0 + 1)
    wt = max(0.0, min(1.0, t_index - t0))
    i0, j0 = int(math.floor(fi)), int(math.floor(fj))
    i1, j1 = min(i0 + 1, g["nlat"] - 1), min(j0 + 1, g["nlon"] - 1)
    di, dj = fi - i0, fj - j0
    nlon = g["nlon"]

    def at(comp: List[List[float]], t: int) -> float:
        c00 = comp[t][i0 * nlon + j0]
        c01 = comp[t][i0 * nlon + j1]
        c10 = comp[t][i1 * nlon + j0]
        c11 = comp[t][i1 * nlon + j1]
        return (c00 * (1 - di) * (1 - dj) + c01 * (1 - di) * dj + c10 * di * (1 - dj) + c11 * di * dj)

    u = at(lvl["u"], t0) * (1 - wt) + at(lvl["u"], t1) * wt
    v = at(lvl["v"], t0) * (1 - wt) + at(lvl["v"], t1) * wt
    return u, v
