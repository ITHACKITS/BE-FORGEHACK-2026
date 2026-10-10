"""
app/api/advice.py

GET /advice/nearby: AI household brief for one location in Indonesia.
"""

from datetime import datetime, timezone
from enum import Enum

from fastapi import APIRouter, Query

from app.services.advice import nearby_advice

router = APIRouter(tags=["analysis"])


class Lang(str, Enum):
    en = "en"
    id = "id"


@router.get("/advice/nearby")
def get_nearby_advice(
    lat: float = Query(..., ge=-12.0, le=7.0, description="Latitude (Indonesia)"),
    lon: float = Query(..., ge=94.0, le=142.0, description="Longitude (Indonesia)"),
    lang: Lang = Query(Lang.en, description="Language of the brief"),
):
    """Facts near the location, the scenario chosen from them, and an LLM-written household brief."""
    result = nearby_advice(lat, lon, lang.value)
    return {"generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), **result}
