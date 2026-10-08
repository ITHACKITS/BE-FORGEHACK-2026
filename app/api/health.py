"""
app/api/health.py

Router untuk status kesehatan sistem dan mode operasional.
"""

from fastapi import APIRouter

from app.core.config import settings
from app.core.offline import is_offline

router = APIRouter(tags=["health"])


@router.get("/health")
def get_health():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "offline_mode": is_offline(),
        "active_sources": {
            "open_meteo": "active (ensemble + offline cache)",
            "firms": "active (offline cache / live API)",
            "worldpop": "active (local 100m grid)",
            "overpass": "active (local facility cache)",
        },
        "disclaimer": settings.DISCLAIMER,
    }
