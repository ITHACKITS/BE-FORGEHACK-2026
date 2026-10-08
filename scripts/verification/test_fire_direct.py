import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.engine.simulator import SimulationRunner
from app.ingest.firms import FirmsIngest
from app.ingest.openmeteo import OpenMeteoIngest
from app.schemas.simulation import SimulationRequest

req = SimulationRequest(
    hazard="fire",
    mode="auto",
    source={"event_id": "live_kalimantan"},
    horizon_hours=48,
    n_members=5,
    seed=42,
    thresholds={"min": 0.9, "mid": 0.5, "max": 0.05}
)

meta_file = BACKEND_DIR / "data" / "events" / "live_kalimantan" / "meta.json"
with open(meta_file, encoding="utf-8") as f:
    event_meta = json.load(f)

weather = OpenMeteoIngest.get_weather_for_simulation("live_kalimantan", n_members=5, seed=42)
hotspots = FirmsIngest.load_event_hotspots("live_kalimantan")
print(f"Loaded {len(hotspots)} hotspots for live_kalimantan")
if hotspots:
    print("Sample hotspot:", hotspots[0])

runner = SimulationRunner(req)
output = runner.run(event_meta, weather, hotspots)
print("Simulation completed!")
print("Run ID:", output["run_id"])
print("Hourly tiers count:", len(output["hourly_tiers"]))
for h in [0, 6, 12, 24]:
    tier_geo = output["hourly_tiers"].get(h, {})
    features = tier_geo.get("features", [])
    print(f"Hour {h}: {len(features)} features")
    for feat in features:
        print("   - Tier:", feat["properties"].get("tier"), "geometry type:", feat["geometry"]["type"])
