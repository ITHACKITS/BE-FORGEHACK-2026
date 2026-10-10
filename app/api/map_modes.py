"""
app/api/map_modes.py

Nationwide map modes: wind field, fire heatmap and smoke paths.
Registered before app/api/layers.py so these paths win over `/layers/{name}`.
All routes are read-only; inputs are enums and bounded integers (422 otherwise).
"""

from datetime import datetime, timezone
from enum import Enum

from fastapi import APIRouter, Query

from app.core.config import settings
from app.services import map_modes, weather_grid

router = APIRouter(tags=["layers"])


class WindLevel(str, Enum):
    surface = "10m"
    ash = "850hPa"


class HeatmapKind(str, Enum):
    fires = "fires"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@router.get("/layers/wind")
def get_wind_field(
    level: WindLevel = Query(WindLevel.surface, description="10m for fire smoke, 850hPa (~1.5 km) for volcanic ash"),
    hours: int = Query(72, ge=0, le=384, description="Forecast window from now, in hours (max 16 days)"),
):
    """
    Wind u/v (m/s) on a 2° grid over Indonesia, 3-hourly from now. `u[t][cell]` with
    cell = i_lat * nlon + i_lon, i_lat from `grid.lat0` northwards and i_lon from `grid.lon0` eastwards.
    """
    data, origin = weather_grid.get_grid()
    if data is None:
        return {
            "available": False,
            "reason": "Wind grid unavailable: offline mode without a stored snapshot.",
            "generated_at": _now(),
        }
    win = weather_grid.window(data, level.value, hours)
    return {
        "available": True,
        "generated_at": _now(),
        "source": data["source"],
        "fetched_at": data["fetched_at"],
        "origin": origin,
        "stale": win["stale"],
        "is_example": False,
        "level": level.value,
        "units": "m/s",
        "step_hours": data["step_hours"],
        "grid": data["grid"],
        "times": win["times"],
        "u": win["u"],
        "v": win["v"],
        "note": "Forecast skill drops after about 7 days; days 8 to 16 are indicative.",
        "disclaimer": settings.DISCLAIMER,
    }


@router.get("/layers/heatmap")
def get_heatmap(
    kind: HeatmapKind = Query(HeatmapKind.fires),
    days: int = Query(7, ge=1, le=7, description="Days ending on the latest detection date"),
):
    """Fire detections aggregated into 0.25° cells (count and summed FRP)."""
    result = map_modes.fire_heatmap(days)
    return {"generated_at": _now(), **result, "disclaimer": settings.DISCLAIMER}


@router.get("/layers/smoke-paths")
def get_smoke_paths(
    hours: int = Query(72, ge=24, le=72, description="Trajectory length in hours"),
):
    """Forward wind trajectories from strong fire clusters and volcanoes at level II or higher."""
    result = map_modes.smoke_paths(hours)
    return {"generated_at": _now(), **result, "disclaimer": settings.DISCLAIMER}
