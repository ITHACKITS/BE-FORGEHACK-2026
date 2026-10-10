"""
app/services/advice.py

AI household brief for one location ("what is near me and what should I do?").

1. Facts, computed here from our own data: nearby volcanoes and their alert level, FIRMS
   fire detections within 10/25/50 km, the nearest fire-prone forest, and how close the
   72 h smoke and ash paths (app/services/map_modes.py) pass, and when.
2. The AI service's RandomForest detection scorer checks the nearby detections.
3. A scenario is chosen from the facts with fixed rules (ash threat, smoke threat,
   prevention, clear).
4. The AI service writes the brief with the Featherless LLM (template fallback).
   Every number in the brief comes from the facts.
"""

from __future__ import annotations

import logging
import math
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings
from app.db.repositories.forest_repo import ForestRepository
from app.db.repositories.volcano_repo import VolcanoRepository
from app.db.session import get_db_connection
from app.services import map_modes

logger = logging.getLogger(__name__)

EARTH_R_KM = 6371.0
SMOKE_NEAR_KM = 50.0
ASH_NEAR_KM = 75.0
FOREST_NEAR_KM = 75.0
VOLCANO_NEAR_KM = 300.0
MAX_SCORED_HOTSPOTS = 20  # the scorer takes ~0.2 s per point
ASH_MIN_LEVEL = 3         # only Level III/IV volcanoes count as an ash threat
NEAR_SOURCE_KM = 20.0     # closest at the source itself only counts when the source is this close
ASH_SOURCE_MAX_KM = 200.0 # farther away, ash thins out; a passing plume centre is not a household threat
SOURCE = (
    "StandbAI database (PVMBG volcanoes, NASA FIRMS detections, fire-prone forests), "
    "72 h smoke/ash paths on the Open-Meteo wind forecast, AI service (RandomForest detection scorer, Featherless LLM)"
)


def _km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_R_KM * math.asin(math.sqrt(a))


def _nearby_hotspots(lat: float, lon: float, radius_km: float = 50.0) -> List[Dict[str, Any]]:
    # Bounding box first (cheap), exact distance after.
    dlat = radius_km / 111.0
    dlon = radius_km / (111.0 * max(0.2, math.cos(math.radians(lat))))
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT latitude, longitude, COALESCE(frp, 0), brightness, confidence, COALESCE(acq_date, '') "
            "FROM hotspots WHERE latitude BETWEEN ? AND ? AND longitude BETWEEN ? AND ?",
            (lat - dlat, lat + dlat, lon - dlon, lon + dlon),
        ).fetchall()
    finally:
        conn.close()
    out = []
    for r in rows:
        d = _km(lat, lon, r[0], r[1])
        if d <= radius_km:
            out.append({"lat": r[0], "lon": r[1], "frp": float(r[2]), "brightness": r[3], "confidence": r[4], "date": r[5], "km": d})
    return sorted(out, key=lambda h: h["km"])


def _direction(lat: float, lon: float, to_lat: float, to_lon: float) -> str:
    """8-point compass direction from the location to a point (N, NE, E, ...)."""
    y = math.sin(math.radians(to_lon - lon)) * math.cos(math.radians(to_lat))
    x = (math.cos(math.radians(lat)) * math.sin(math.radians(to_lat))
         - math.sin(math.radians(lat)) * math.cos(math.radians(to_lat)) * math.cos(math.radians(to_lon - lon)))
    bearing = (math.degrees(math.atan2(y, x)) + 360) % 360
    return ["N", "NE", "E", "SE", "S", "SW", "W", "NW"][round(bearing / 45) % 8]


def _closest_approach(lat: float, lon: float, coords: List[List[float]]) -> tuple[float, int]:
    """Smallest distance (km) between the location and an hourly path, and the hour it happens."""
    best, hour = float("inf"), 0
    for h, (plat, plon) in enumerate(coords):
        d = _km(lat, lon, plat, plon)
        if d < best:
            best, hour = d, h
    return best, hour


def _ai_detection_check(hotspots: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Ask the AI service's RandomForest scorer whether the nearby detections look like real fires."""
    pts = hotspots[:MAX_SCORED_HOTSPOTS]
    if not pts or settings.OFFLINE:
        return None
    body = {"points": [
        {"latitude": h["lat"], "longitude": h["lon"], "frp": h["frp"],
         "brightness": h["brightness"], "confidence": _confidence(h["confidence"]), "is_day": True}
        for h in pts
    ]}
    try:
        r = httpx.post(f"{settings.AI_SERVICE_URL.rstrip('/')}/api/v1/fire/predict-batch", json=body, timeout=10.0)
        r.raise_for_status()
        data = r.json()
        preds = data.get("predictions", [])
        return {
            "checked": len(preds),
            "fire_like": sum(1 for p in preds if p.get("is_fire")),
            "model": (preds[0].get("model_engine") if preds else None) or "RandomForest (NASA FIRMS)",
        }
    except Exception as e:
        logger.warning("AI detection check failed: %s", type(e).__name__)
        return None


def _confidence(value: Any) -> Optional[float]:
    """FIRMS confidence is a number (MODIS) or l/n/h (VIIRS); the scorer wants 0-100."""
    if value is None:
        return None
    text = str(value).strip().lower()
    mapping = {"l": 30.0, "low": 30.0, "n": 60.0, "nominal": 60.0, "h": 90.0, "high": 90.0}
    if text in mapping:
        return mapping[text]
    try:
        return max(0.0, min(100.0, float(text)))
    except ValueError:
        return None


def nearby_facts(lat: float, lon: float) -> Dict[str, Any]:
    facts: Dict[str, Any] = {"location": {"lat": round(lat, 4), "lon": round(lon, 4)}}

    # Volcanoes within 300 km, nearest first.
    volcs = []
    for v in VolcanoRepository.get_all():
        d = _km(lat, lon, v["latitude"], v["longitude"])
        if d <= VOLCANO_NEAR_KM:
            radius = float(v.get("radius_bahaya_km") or 0)
            volcs.append({
                "name": v["name"], "level": int(v.get("level") or 1), "distance_km": round(d, 1),
                "danger_radius_km": radius, "inside_danger_zone": radius > 0 and d <= radius,
            })
    facts["volcanoes_nearby"] = sorted(volcs, key=lambda x: x["distance_km"])[:3]

    # Fire detections within 50 km.
    hs = _nearby_hotspots(lat, lon)
    facts["hotspots"] = {
        "within_10km": sum(1 for h in hs if h["km"] <= 10),
        "within_25km": sum(1 for h in hs if h["km"] <= 25),
        "within_50km": len(hs),
        "nearest_km": round(hs[0]["km"], 1) if hs else None,
        "max_frp_mw": round(max(h["frp"] for h in hs)) if hs else None,
        "latest_date": max(h["date"] for h in hs) if hs else None,
    }
    facts["ai_detection_check"] = None  # filled in by nearby_advice, in parallel with the brief
    facts["_hotspots_for_check"] = hs[:MAX_SCORED_HOTSPOTS]

    # Nearest fire-prone forest or peatland.
    forest = None
    for f in ForestRepository.get_all():
        if f.get("lat") is None or f.get("lon") is None:
            continue
        d = _km(lat, lon, f["lat"], f["lon"])
        if d <= FOREST_NEAR_KM and (forest is None or d < forest["distance_km"]):
            forest = {"name": f["name"], "distance_km": round(d, 1), "risk": f.get("risk_level")}
    facts["fire_prone_forest"] = forest

    # 72 h smoke (fire clusters) and ash (volcanoes level II+) paths that pass close by.
    paths = map_modes.smoke_paths(72)
    smoke = ash = None
    for p in paths.get("paths", []):
        dist, hour = _closest_approach(lat, lon, p.get("coords") or [])
        # Closest at hour 0 means the plume only drifts away from here: it matters only when the
        # source itself is close (no arrival time then).
        if hour == 0 and dist > NEAR_SOURCE_KM:
            continue
        src = p.get("source") or {}
        src_km = _km(lat, lon, src.get("lat", lat), src.get("lon", lon))
        where = {
            "source_distance_km": round(src_km, 1),
            "source_direction": _direction(lat, lon, src.get("lat", lat), src.get("lon", lon)),
            "hours_from_now": hour if hour > 0 else None,
            "near_source": hour == 0,
        }
        if p["source_type"] == "fire" and dist <= SMOKE_NEAR_KM and (smoke is None or dist < smoke["closest_km"]):
            smoke = {"source": "fire cluster", "closest_km": round(dist, 1), **where}
        if (p["source_type"] == "volcano" and (p.get("level") or 0) >= ASH_MIN_LEVEL and dist <= ASH_NEAR_KM
                and src_km <= ASH_SOURCE_MAX_KM and (ash is None or dist < ash["closest_km"])):
            ash = {"source": p["name"], "level": p.get("level"), "closest_km": round(dist, 1), **where}
    facts["smoke_forecast"] = smoke
    facts["ash_forecast"] = ash
    facts["data_as_of"] = {"fires": paths.get("fires_as_of"), "wind": paths.get("wind_fetched_at")}
    return facts


def choose_scenario(f: Dict[str, Any]) -> str:
    """Fixed rules, most urgent first."""
    hs = f.get("hotspots") or {}
    volc_threat = any(
        (v["level"] >= 2 and v["inside_danger_zone"]) or (v["level"] >= 3 and v["distance_km"] <= 30)
        for v in f.get("volcanoes_nearby") or []
    )
    if volc_threat or f.get("ash_forecast"):
        return "ash_threat"
    if hs.get("within_25km", 0) >= 1 or hs.get("within_50km", 0) >= 5 or f.get("smoke_forecast"):
        return "smoke_threat"
    if f.get("fire_prone_forest") or hs.get("within_50km", 0) >= 1:
        return "prevention"
    return "clear"


def _brief(scenario: str, lang: str, facts: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        r = httpx.post(
            f"{settings.AI_SERVICE_URL.rstrip('/')}/api/v1/brief",
            json={"scenario": scenario, "lang": lang, "facts": facts},
            timeout=30.0,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.warning("AI brief failed: %s", type(e).__name__)
        return None


def nearby_advice(lat: float, lon: float, lang: str) -> Dict[str, Any]:
    facts = nearby_facts(lat, lon)
    to_check = facts.pop("_hotspots_for_check")
    scenario = choose_scenario(facts)
    brief = None
    if not settings.OFFLINE:
        # The detection scorer and the LLM brief are independent: run them side by side.
        with ThreadPoolExecutor(max_workers=2) as pool:
            check = pool.submit(_ai_detection_check, to_check)
            written = pool.submit(_brief, scenario, lang, dict(facts))
            facts["ai_detection_check"] = check.result()
            brief = written.result()
    return {"scenario": scenario, "facts": facts, "brief": brief, "source": SOURCE, "is_example": False, "disclaimer": settings.DISCLAIMER}
