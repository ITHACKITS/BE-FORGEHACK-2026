"""
app/api/attributions.py

Data source attributions and licences (AGENTS.md principle 9).
"""

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["attributions"])


@router.get("/attributions")
def get_attributions():
    return {
        "project": settings.PROJECT_NAME,
        "description": (
            "Data sources and licences behind Standbai's wildfire smoke and volcanic ash "
            "forecasts and preparedness guidance for Indonesia."
        ),
        "attributions": [
            {
                "source": "WorldPop (School of Geography and Environmental Science, University of Southampton)",
                "data": "Age and sex structures, 100m resolution (2020)",
                "license": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
                "url": "https://hub.worldpop.org/geodata/summary?id=24798"
            },
            {
                "source": "OpenStreetMap Contributors",
                "data": "Airports and water bodies",
                "license": "Open Database License (ODbL) 1.0",
                "url": "https://www.openstreetmap.org/copyright"
            },
            {
                "source": "Open-Meteo",
                "data": "Ensemble Weather API (DWD ICON, GFS, ECMWF IFS)",
                "license": "Non-Commercial / Attribution Open Data",
                "url": "https://open-meteo.com/en/docs/ensemble-api"
            },
            {
                "source": "NASA FIRMS (EOSDIS)",
                "data": "VIIRS & MODIS Near Real-Time Active Fire / Hotspot & FRP",
                "license": "NASA Open Data Policy",
                "url": "https://firms.modaps.eosdis.nasa.gov"
            },
            {
                "source": "OpenAQ",
                "data": "Air Quality Open Monitoring Platform",
                "license": "Open Data Commons Open Database License (ODbL)",
                "url": "https://openaq.org"
            },
            {
                "source": "Kementerian Lingkungan Hidup dan Kehutanan (KLHK, Ministry of Environment and Forestry)",
                "data": "Minister of Environment and Forestry Regulation No. P.14/2020 on the Air Pollutant Standard Index (ISPU)",
                "license": "Public document of the Republic of Indonesia",
                "url": "https://peraturan.go.id/files/bn774-2020.pdf"
            },
            {
                "source": "Badan Geologi / PVMBG (Ministry of Energy and Mineral Resources)",
                "data": "Eruption reports and activity status of Anak Krakatau",
                "license": "Badan Geologi public information",
                "url": "https://geologi.esdm.go.id"
            }
        ]
    }
