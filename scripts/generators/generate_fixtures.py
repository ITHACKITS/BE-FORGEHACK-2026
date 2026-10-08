"""
scripts/generate_fixtures.py

Menghasilkan contoh respons API nyata dari FastAPI TestClient
dan menyimpannya ke docs/fixtures/*.json untuk API_CONTRACT.md.
"""

import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
FIXTURES_DIR = BACKEND_DIR / "docs" / "fixtures"
FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

def save_fixture(name: str, data: dict):
    path = FIXTURES_DIR / f"{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {path}")

# 1. Health
save_fixture("health", client.get("/health").json())

# 2. Events
save_fixture("events", client.get("/events").json())

# 3. Attributions
save_fixture("attributions", client.get("/attributions").json())

# 4. Simulate Volcano
volcano_sim = client.post("/simulate", json={
    "hazard": "volcano",
    "mode": "auto",
    "source": {"event_id": "anak_krakatau_2026_09"},
    "horizon_hours": 6,
    "n_members": 5,
    "seed": 42
}).json()
save_fixture("simulate_volcano", volcano_sim)
v_run_id = volcano_sim["run_id"]

# 5. Tiers
save_fixture("tiers_t12", client.get(f"/runs/{v_run_id}/tiers?t=6").json())

# 6. Impact
save_fixture("impact_volcano", client.get(f"/runs/{v_run_id}/impact").json())

# 7. Land & Water
save_fixture("land_water", client.get(f"/runs/{v_run_id}/land-water").json())

# 8. Rain Effect
save_fixture("rain_effect", client.get(f"/runs/{v_run_id}/rain-effect").json())

# 9. Advice
save_fixture("advice", client.get(f"/runs/{v_run_id}/advice").json())

# 10. Sensitivity
save_fixture("sensitivity", client.post("/runs/sensitivity", json={
    "run_id": v_run_id,
    "parameter_name": "column_height_km"
}).json())

# 11. Simulate Fire
fire_sim = client.post("/simulate", json={
    "hazard": "fire",
    "mode": "auto",
    "source": {"event_id": "live_kalimantan"},
    "horizon_hours": 6,
    "n_members": 5,
    "seed": 42
}).json()
save_fixture("simulate_fire", fire_sim)
f_run_id = fire_sim["run_id"]

# 12. Carbon
save_fixture("carbon_fire", client.get(f"/runs/{f_run_id}/carbon").json())

# 13. Ranking
ranking = client.get(f"/runs/{f_run_id}/ranking").json()
save_fixture("ranking_fire", ranking)

# 14. Extinguish
if ranking.get("ranked_clusters"):
    top_cid = ranking["ranked_clusters"][0]["cluster_id"]
    save_fixture("extinguish_fire", client.post("/fire/extinguish", json={
        "run_id": f_run_id,
        "extinguish_cluster_ids": [top_cid]
    }).json())

# 15. Compare
exp_sim = client.post("/simulate", json={
    "hazard": "volcano",
    "mode": "experiment",
    "source": {"event_id": "anak_krakatau_2026_09"},
    "horizon_hours": 6,
    "n_members": 5,
    "seed": 42,
    "overrides": {"column_height_km": 15.0}
}).json()
v_run_b_id = exp_sim["run_id"]
save_fixture("compare_runs", client.post("/runs/compare", json={
    "run_id_a": v_run_id,
    "run_id_b": v_run_b_id
}).json())

# 16. Validation Krakatau
save_fixture("validation_krakatau", client.get("/validation/anak_krakatau_2026_09").json())

# 17. Validation Kalimantan
save_fixture("validation_kalimantan", client.get("/validation/live_kalimantan").json())

# 18. Limits
save_fixture("limits", client.get("/limits").json())

# 19. Sources
save_fixture("sources", client.get("/sources").json())

# 20. Demo Play
save_fixture("demo_play", client.get("/demo/play/anak_krakatau_2026_09").json())

# 21. Export JSON
save_fixture("export_summary", client.get(f"/runs/{v_run_id}/export?format=json").json())

# 22. Lahar Warning
save_fixture("lahar_warning", client.get(f"/runs/{v_run_id}/lahar-warning").json())

print("All fixtures generated successfully!")
