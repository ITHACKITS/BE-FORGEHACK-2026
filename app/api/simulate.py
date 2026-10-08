"""
app/api/simulate.py

Router untuk eksekusi simulasi, polling status, poligon tiga tingkat, dan kartu dampak.
Mematuhi seluruh prinsip AGENTS.md (penolakan overrides pada mode auto, determinisme, label skenario).
"""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query

from app.api.events import NATIONAL_KARHUTLA
from app.core.config import BACKEND_DIR, EVENTS_DIR, RUNS_DIR
from app.engine.grid import SimulationGrid
from app.engine.simulator import SimulationRunner
from app.impact.exposure import (
    calculate_impact_ranges,
    evaluate_decision_card,
    get_exposed_facilities_list,
    get_health_and_mask_guidance,
)
from app.ingest.firms import FirmsIngest
from app.ingest.openmeteo import OpenMeteoIngest
from app.schemas.simulation import SimulationRequest

router = APIRouter(tags=["simulation"])

# In-memory store untuk run aktif yang membawa array lengkap (dibatasi 10 entri untuk mencegah kebocoran memori)
RUNS_CACHE: Dict[str, Dict[str, Any]] = {}


@router.post("/simulate")
def start_simulation(req: SimulationRequest):
    import datetime
    import json

    import numpy as np

    event_id = (req.source.event_id or "").strip()
    if not event_id:
        if req.source.latitude is not None and req.source.longitude is not None:
            import hashlib
            coord_hash = hashlib.md5(f"{float(req.source.latitude):.4f}_{float(req.source.longitude):.4f}".encode()).hexdigest()[:8]
            event_id = f"custom_{req.hazard}_{coord_hash}"
        else:
            event_id = "hutan_sebangau" if req.hazard == "fire" else "anak_krakatau_2026_09"

    event_dir = EVENTS_DIR / event_id
    meta_file = event_dir / "meta.json"

    # 1. Muat metadata kejadian (Otomatis bangun metadata jika event berasal dari katalog nasional atau titik kustom)
    if meta_file.exists():
        event_meta = json.loads(meta_file.read_text(encoding="utf-8-sig"))
    else:
        # Cek apakah ada direktori di data/events yang cocok (toleran terhadap perbedaan underscore)
        clean_eid = event_id.replace("_", "").lower()
        if EVENTS_DIR.exists():
            for d in EVENTS_DIR.iterdir():
                if d.is_dir() and d.name.replace("_", "").lower() == clean_eid:
                    mf = d / "meta.json"
                    if mf.exists():
                        try:
                            event_meta = json.loads(mf.read_text(encoding="utf-8-sig"))
                            meta_file = mf
                            event_dir = d
                            event_id = d.name
                            break
                        except Exception:
                            pass

    if not event_meta:
        # Cek apakah event_id ada di database katalog gunung api nasional
        volc_feature = None
        try:
            from app.db.repositories.volcano_repo import VolcanoRepository
            v_obj = VolcanoRepository.get_by_id(event_id)
            if v_obj:
                volc_feature = {
                    "properties": v_obj,
                    "geometry": {"coordinates": [v_obj["longitude"], v_obj["latitude"]]}
                }
        except Exception:
            pass

        if not volc_feature:
            volc_path = BACKEND_DIR / "data" / "layers" / "volcanoes_indonesia.geojson"
            if volc_path.exists():
                try:
                    geo = json.loads(volc_path.read_text(encoding="utf-8-sig"))
                    clean_e = event_id.replace("_", "").lower()
                    for feat in geo.get("features", []):
                        f_id = (feat.get("properties", {}).get("id") or "").lower()
                        f_ev = (feat.get("properties", {}).get("event_id") or "").lower()
                        clean_fid = f_id.replace("_", "")
                        clean_fev = f_ev.replace("_", "")
                        if clean_fid == clean_e or clean_fev == clean_e or clean_fid.startswith(clean_e) or clean_e in clean_fid:
                            volc_feature = feat
                            break
                except Exception:
                    pass

        if volc_feature:
            p = volc_feature["properties"]
            c = volc_feature["geometry"]["coordinates"]
            event_meta = {
                "event_id": event_id,
                "hazard": "volcano",
                "name": f"Erupsi {p['name']} ({p['province']})",
                "start_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "duration_h": 24.0,
                "alert_level_at_event": p.get("level_name", "Level III (Siaga)"),
                "restricted_radius_km": p.get("radius_bahaya_km", 5.0),
                "column_height_km": 8.0,
                "plume_top_asl_km": 12.0,
                "vent_elevation_m": float(p.get("elevation_m", 1500.0)),
                "coordinates": {"latitude": float(c[1]), "longitude": float(c[0])},
                "bbox": [float(c[0]) - 0.7, float(c[1]) - 0.7, float(c[0]) + 0.7, float(c[1]) + 0.7],
                "source": "PVMBG Badan Geologi ESDM RI (Katalog 70 Gunung Api Nasional)",
                "members_source": "open_meteo_live_forecast_api",
                "n_members": req.n_members,
                "data_status": {
                    "weather": "open_meteo_live_or_ensemble",
                    "vona": "pvmbg_national_catalog",
                    "column_height": "estimated_standard"
                }
            }
            event_dir.mkdir(parents=True, exist_ok=True)
            meta_file.write_text(json.dumps(event_meta, indent=2, ensure_ascii=False), encoding="utf-8")

        elif event_id in NATIONAL_KARHUTLA:
            k = NATIONAL_KARHUTLA[event_id]
            coords = k.get("coordinates", {})
            k_lat = float(coords.get("latitude") if "latitude" in coords else k.get("lat", -2.5))
            k_lon = float(coords.get("longitude") if "longitude" in coords else k.get("lon", 113.5))
            event_meta = {
                "event_id": event_id,
                "hazard": "fire",
                "name": k["name"],
                "province": k.get("province", "Indonesia"),
                "start_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "duration_h": 24.0,
                "coordinates": {"latitude": k_lat, "longitude": k_lon},
                "bbox": [k_lon - 0.7, k_lat - 0.7, k_lon + 0.7, k_lat + 0.7],
                "source": "NASA FIRMS NRT (Zona Karhutla Nasional)",
                "members_source": "open_meteo_live_forecast_api",
                "n_members": req.n_members,
                "data_status": {
                    "weather": "open_meteo_live_or_ensemble",
                    "firms": "live_nrt_cluster"
                }
            }
            event_dir.mkdir(parents=True, exist_ok=True)
            meta_file.write_text(json.dumps(event_meta, indent=2, ensure_ascii=False), encoding="utf-8")

        elif req.source.latitude is not None and req.source.longitude is not None:
            # Mode Simulasi Titik Bebas / Klik Sembarang Peta Indonesia
            c_lat = float(req.source.latitude)
            c_lon = float(req.source.longitude)
            c_name = req.source.name or f"Titik Kustom ({c_lat:.3f}, {c_lon:.3f})"
            event_meta = {
                "event_id": event_id,
                "hazard": req.hazard,
                "name": c_name,
                "start_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "duration_h": 24.0,
                "column_height_km": 6.0 if req.hazard == "volcano" else None,
                "vent_elevation_m": 800.0 if req.hazard == "volcano" else None,
                "coordinates": {"latitude": c_lat, "longitude": c_lon},
                "bbox": [c_lon - 0.7, c_lat - 0.7, c_lon + 0.7, c_lat + 0.7],
                "source": "Koordinat Kustom Pengguna (Interaktif)",
                "members_source": "open_meteo_live_forecast_api",
                "n_members": req.n_members
            }
            event_dir.mkdir(parents=True, exist_ok=True)
            meta_file.write_text(json.dumps(event_meta, indent=2, ensure_ascii=False), encoding="utf-8")

        else:
            # Cek database katalog 36 hutan nasional
            forest_obj = None
            try:
                from app.db.repositories.forest_repo import ForestRepository
                db_f = ForestRepository.get_by_id(event_id)
                if db_f:
                    forest_obj = db_f
            except Exception:
                pass

            if not forest_obj:
                forest_path = BACKEND_DIR / "data" / "layers" / "forests_indonesia.json"
                if forest_path.exists():
                    try:
                        f_data = json.loads(forest_path.read_text(encoding="utf-8-sig"))
                        f_list = f_data if isinstance(f_data, list) else f_data.get("forests", [])
                        clean_e = event_id.lower().replace("_", "")
                        for f_item in f_list:
                            fid = (f_item.get("id") or "").lower()
                            clean_fid = fid.replace("_", "")
                            if clean_fid == clean_e or clean_fid.startswith(clean_e) or clean_e in clean_fid:
                                forest_obj = f_item
                                break
                    except Exception:
                        pass

            if forest_obj:
                f_lat = float(forest_obj.get("lat") or forest_obj.get("latitude") or 0.0)
                f_lon = float(forest_obj.get("lon") or forest_obj.get("longitude") or 0.0)
                event_meta = {
                    "event_id": event_id,
                    "hazard": "fire",
                    "name": forest_obj["name"],
                    "province": forest_obj.get("province", "Indonesia"),
                    "start_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "duration_h": 24.0,
                    "coordinates": {"latitude": f_lat, "longitude": f_lon},
                    "bbox": [f_lon - 0.7, f_lat - 0.7, f_lon + 0.7, f_lat + 0.7],
                    "source": "Katalog 36 Kawasan Hutan & Konservasi Nasional",
                    "members_source": "open_meteo_live_forecast_api",
                    "n_members": req.n_members,
                    "data_status": {"weather": "open_meteo_live_or_ensemble", "firms": "live_nrt_cluster"}
                }
                event_dir.mkdir(parents=True, exist_ok=True)
                meta_file.write_text(json.dumps(event_meta, indent=2, ensure_ascii=False), encoding="utf-8")
            else:
                raise HTTPException(status_code=404, detail=f"Event '{event_id}' tidak ditemukan di data/events/ maupun katalog nasional.")

    # 2. Muat data cuaca
    try:
        weather_data = OpenMeteoIngest.get_weather_for_simulation(
            event_id=event_id,
            n_members=req.n_members,
            seed=req.seed,
            overrides=req.overrides
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memuat cuaca: {e}")

    # 3. Muat titik api jika hazard kebakaran
    hotspots = []
    if req.hazard == "fire":
        hotspots = FirmsIngest.load_event_hotspots(event_id, overrides=req.overrides)
        total_frp = sum(float(h.get("frp", 0.0)) for h in hotspots)

        # Jika titik api lokal minim / kosong, periksa apakah terdapat titik api riil satelit FIRMS
        # yang jatuh di dalam poligon batas kawasan resmi (Point-in-Polygon query)
        if len(hotspots) < 10 and not (req.overrides and "hotspots" in req.overrides):
            f_geom = None
            try:
                from app.db.repositories.forest_repo import ForestRepository
                db_forest = ForestRepository.get_by_id(event_id)
                if db_forest and db_forest.get("geometry"):
                    f_geom = db_forest["geometry"]
            except Exception:
                pass

            if not f_geom:
                bound_path = BACKEND_DIR / "data" / "layers" / "forest_boundaries.geojson"
                if bound_path.exists():
                    try:
                        b_data = json.loads(bound_path.read_text(encoding="utf-8"))
                        f_feat = next((feat for feat in b_data.get("features", []) if feat.get("id") == event_id), None)
                        if f_feat:
                            f_geom = f_feat["geometry"]
                    except Exception:
                        pass

            if f_geom:
                try:
                    from shapely.geometry import Point, shape
                    f_poly = shape(f_geom)
                    nat_hotspots = FirmsIngest.load_event_hotspots("national")
                    inside_pts = [h for h in nat_hotspots if f_poly.contains(Point(h["longitude"], h["latitude"]))]
                    if len(inside_pts) > len(hotspots):
                        hotspots = inside_pts
                        total_frp = sum(float(h.get("frp", 0.0)) for h in hotspots)
                except Exception:
                    pass

        # Jika mode 'experiment' (skenario uji coba) atau custom point dan belum ada titik api signifikan (< 40 MW),
        # sediakan klaster titik api skenario agar pengguna dapat mengamati simulasi dispersi asap
        if (req.mode == "experiment" and total_frp < 40.0) or (not hotspots and req.mode == "experiment") or (not hotspots and req.source.latitude is not None):
            coords = event_meta.get("coordinates", {})
            c_lat = coords.get("latitude") or coords.get("center_lat", -2.5)
            c_lon = coords.get("longitude") or coords.get("center_lon", 113.5)
            rng_f = np.random.default_rng(req.seed)
            hotspots = []
            for i in range(18):
                d_lat = float(rng_f.normal(0, 0.04))
                d_lon = float(rng_f.normal(0, 0.04))
                frp_val = float(rng_f.uniform(45.0, 160.0))
                hotspots.append({
                    "id": f"scenario_hotspot_{i}",
                    "latitude": float(c_lat + d_lat),
                    "longitude": float(c_lon + d_lon),
                    "frp": frp_val,
                    "confidence": "high",
                    "acq_date": "scenario_experiment",
                    "acq_time": "1200",
                    "is_active": True
                })

    # 4. Jalankan simulator
    runner = SimulationRunner(req)
    run_output = runner.run(event_meta, weather_data, hotspots)

    # Simpan di memori dengan pembatasan LRU (maksimal 10 run)
    if len(RUNS_CACHE) >= 10:
        oldest_key = next(iter(RUNS_CACHE))
        del RUNS_CACHE[oldest_key]
    RUNS_CACHE[runner.run_id] = run_output

    return {
        "run_id": runner.run_id,
        "hazard": req.hazard,
        "mode": req.mode,
        "status": "completed",
        "scenario_label": run_output["scenario_label"],
        "members_source": run_output["members_source"],
        "n_members": req.n_members,
        "seed": req.seed,
        "created_at_utc": runner.created_at_utc,
        "disclaimer": run_output["disclaimer"],
        "assumptions_used": run_output["assumptions_used"],
    }


def _get_run_data(run_id: str) -> Dict[str, Any]:
    if run_id in RUNS_CACHE:
        return RUNS_CACHE[run_id]

    # Coba muat dari file
    save_file = RUNS_DIR / f"{run_id}.json"
    if not save_file.exists():
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' tidak ditemukan.")

    import json
    return json.loads(save_file.read_text(encoding="utf-8-sig"))


@router.get("/runs/{run_id}")
def get_run_status(run_id: str):
    data = _get_run_data(run_id)
    return {
        "run_id": data["run_id"],
        "hazard": data["hazard"],
        "mode": data["mode"],
        "event_id": data["event_id"],
        "status": data["status"],
        "scenario_label": data["scenario_label"],
        "members_source": data["members_source"],
        "n_members": data["n_members"],
        "seed": data["seed"],
        "created_at_utc": data["created_at_utc"],
        "completed_at_utc": data.get("completed_at_utc"),
        "disclaimer": data["disclaimer"],
        "assumptions_used": data.get("assumptions_used", []),
    }


@router.get("/runs/{run_id}/tiers")
def get_run_tiers(run_id: str, t: int = Query(0, ge=0, le=48, description="Langkah jam")):
    data = _get_run_data(run_id)
    tiers = data.get("hourly_tiers", {})
    # Key di JSON file mungkin berupa string
    step_key = str(t) if str(t) in tiers else t
    if step_key not in tiers:
        # Kembalikan FeatureCollection kosong yang valid jika di luar jam
        return {
            "type": "FeatureCollection",
            "properties": {"hour": t, "thresholds": {"min": 0.9, "mid": 0.5, "max": 0.05}},
            "features": []
        }
    return tiers[step_key]


@router.get("/runs/{run_id}/impact")
def get_run_impact(run_id: str):
    if run_id not in RUNS_CACHE:
        raise HTTPException(status_code=404, detail=f"Data array run '{run_id}' tidak aktif di memori.")

    data = RUNS_CACHE[run_id]
    grid_meta = data["grid"]
    grid = SimulationGrid(
        lat_min=grid_meta["lat_min"],
        lat_max=grid_meta["lat_max"],
        lon_min=grid_meta["lon_min"],
        lon_max=grid_meta["lon_max"],
        resolution_deg=grid_meta["resolution_deg"],
    )

    return calculate_impact_ranges(data, grid)


@router.get("/runs/{run_id}/location/{facility_id}")
def get_location_decision_card(run_id: str, facility_id: str):
    if run_id not in RUNS_CACHE:
        raise HTTPException(status_code=404, detail=f"Data array run '{run_id}' tidak aktif di memori.")

    data = RUNS_CACHE[run_id]
    grid_meta = data["grid"]
    grid = SimulationGrid(
        lat_min=grid_meta["lat_min"],
        lat_max=grid_meta["lat_max"],
        lon_min=grid_meta["lon_min"],
        lon_max=grid_meta["lon_max"],
        resolution_deg=grid_meta["resolution_deg"],
    )

    return evaluate_decision_card(data, facility_id, grid)


@router.get("/runs/{run_id}/facilities-impacted")
def get_run_facilities_impacted(run_id: str, min_prob: float = Query(0.05, ge=0.01, le=1.0)):
    if run_id not in RUNS_CACHE:
        raise HTTPException(status_code=404, detail=f"Data array run '{run_id}' tidak aktif di memori.")

    data = RUNS_CACHE[run_id]
    grid_meta = data["grid"]
    grid = SimulationGrid(
        lat_min=grid_meta["lat_min"],
        lat_max=grid_meta["lat_max"],
        lon_min=grid_meta["lon_min"],
        lon_max=grid_meta["lon_max"],
        resolution_deg=grid_meta["resolution_deg"],
    )

    return get_exposed_facilities_list(data, grid, min_prob=min_prob)


@router.get("/runs/{run_id}/health-guidance")
def get_run_health_guidance(run_id: str):
    data = _get_run_data(run_id)
    hazard = data.get("hazard", "volcano")
    return get_health_and_mask_guidance(hazard=hazard)
