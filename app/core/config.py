"""
app/core/config.py

Application settings and loaders for the assumption and hazard files.
Settings come from environment variables; a local `.env` is loaded first if present.
API keys are read here and never logged or returned.
"""

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

from app.core.offline import is_offline

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent

# Variables already set in the environment take precedence over `.env`.
load_dotenv(BACKEND_DIR / ".env", override=False)

CONFIG_DIR = BACKEND_DIR / "config"
DATA_DIR = BACKEND_DIR / "data"
EVENTS_DIR = DATA_DIR / "events"
RUNS_DIR = DATA_DIR / "runs"
DOCS_DIR = BACKEND_DIR / "docs"

# Make sure the run output folder exists
RUNS_DIR.mkdir(parents=True, exist_ok=True)


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings:
    PROJECT_NAME: str = "Standbai"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api"
    DESCRIPTION: str = (
        "Standbai forecasts where wildfire smoke and volcanic ash will travel over Indonesia "
        "and what families should prepare before it arrives. A tool for learning and preparing, "
        "not an official warning."
    )
    FIRMS_MAP_KEY: str | None = os.environ.get("FIRMS_MAP_KEY")
    OPENAQ_API_KEY: str | None = os.environ.get("OPENAQ_API_KEY")
    AI_SERVICE_URL: str = os.environ.get("AI_SERVICE_URL", "http://localhost:8001")
    AI_INTERNAL_TOKEN: str | None = os.environ.get("AI_INTERNAL_TOKEN")
    JOB_TOKEN: str | None = os.environ.get("JOB_TOKEN")
    N8N_ALERT_WEBHOOK_URL: str | None = os.environ.get("N8N_ALERT_WEBHOOK_URL")
    N8N_WEBHOOK_SECRET: str | None = os.environ.get("N8N_WEBHOOK_SECRET")
    CORS_ORIGINS: list[str] = _split_csv(os.environ.get("CORS_ORIGINS", "http://localhost:5173"))
    PUBLIC_APP_URL: str = os.environ.get("PUBLIC_APP_URL", "http://localhost:5173")
    USER_AGENT: str = "Standbai/1.0 (+https://github.com/ITHACKITS/BE-FORGEHACK-2026)"

    DISCLAIMER: str = (
        "Not an official warning. Follow BMKG, PVMBG and your local BPBD. "
        "Standbai is a science-based estimate for learning and preparing."
    )

    @property
    def OFFLINE(self) -> bool:
        return is_offline()


settings = Settings()


def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8-sig") as f:
        return yaml.safe_load(f) or {}


_assumptions_cache = None
_hazards_cache = None


def get_assumptions() -> Dict[str, Any]:
    global _assumptions_cache
    if _assumptions_cache is None:
        _assumptions_cache = load_yaml(CONFIG_DIR / "assumptions.yaml")
    return _assumptions_cache


def get_hazards() -> Dict[str, Any]:
    global _hazards_cache
    if _hazards_cache is None:
        _hazards_cache = load_yaml(CONFIG_DIR / "hazards.yaml")
    return _hazards_cache


def get_assumptions_used(keys: list[str] | None = None) -> list[Dict[str, Any]]:
    """
    Return the parameters used together with their evidence status,
    restricted to `keys` when given.
    """
    assumptions = get_assumptions()
    result = []
    target_keys = keys if keys is not None else list(assumptions.keys())

    for k in target_keys:
        item = assumptions.get(k)
        if item and isinstance(item, dict):
            status = item.get("status", "assumption_placeholder")
            result.append({
                "parameter": k,
                "value": item.get("value"),
                "status": status,
                "source": item.get("source"),
                "caveat": item.get("caveat"),
            })
    return result


get_assumptions_list = get_assumptions_used


def is_pm25_emission_factor_sourced() -> bool:
    """
    AGENTS.md principle 11: engine-derived ISPU categories are computed only
    when the PM2.5 emission factor (D13b) has a `sourced*` status.
    """
    assumptions = get_assumptions()
    ef_item = assumptions.get("emission_factor_pm25_g_per_kg", {})
    status = ef_item.get("status", "")
    return status.startswith("sourced")
