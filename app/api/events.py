"""
app/api/events.py

Router untuk daftar kejadian siap pakai (Pre-configured Events).
"""

import json

from fastapi import APIRouter, HTTPException

from app.core.config import BACKEND_DIR, EVENTS_DIR

router = APIRouter(tags=["events"])

NATIONAL_KARHUTLA = {
    "live_kalimantan": {
        "event_id": "live_kalimantan",
        "hazard": "fire",
        "name": "Karhutla Gambut Kalimantan (NASA FIRMS NRT)",
        "province": "Kalimantan Tengah",
        "coordinates": {"latitude": -2.5, "longitude": 113.5}
    },
    "karhutla_riau": {
        "event_id": "karhutla_riau",
        "hazard": "fire",
        "name": "Karhutla Gambut Riau (Siak & Pelalawan)",
        "province": "Riau",
        "coordinates": {"latitude": 0.75, "longitude": 101.85}
    },
    "karhutla_sumsel": {
        "event_id": "karhutla_sumsel",
        "hazard": "fire",
        "name": "Karhutla Gambut Sumatera Selatan (OKI)",
        "province": "Sumatera Selatan",
        "coordinates": {"latitude": -3.45, "longitude": 105.15}
    },
    "karhutla_jambi": {
        "event_id": "karhutla_jambi",
        "hazard": "fire",
        "name": "Karhutla Gambut Jambi (Muaro Jambi)",
        "province": "Jambi",
        "coordinates": {"latitude": -1.45, "longitude": 103.80}
    },
    "karhutla_kalbar": {
        "event_id": "karhutla_kalbar",
        "hazard": "fire",
        "name": "Karhutla Gambut Kalimantan Barat (Ketapang)",
        "province": "Kalimantan Barat",
        "coordinates": {"latitude": -1.85, "longitude": 109.85}
    },
    "karhutla_kalsel": {
        "event_id": "karhutla_kalsel",
        "hazard": "fire",
        "name": "Karhutla Gambut Kalimantan Selatan (Banjarbaru)",
        "province": "Kalimantan Selatan",
        "coordinates": {"latitude": -3.45, "longitude": 114.85}
    },
    "karhutla_papua": {
        "event_id": "karhutla_papua",
        "hazard": "fire",
        "name": "Karhutla Savana Papua Selatan (Merauke)",
        "province": "Papua Selatan",
        "coordinates": {"latitude": -8.45, "longitude": 140.40}
    }
}

# Muat 36 Kawasan Hutan & Konservasi Nasional dari forests_indonesia.json jika tersedia
_forests_path = BACKEND_DIR / "data" / "layers" / "forests_indonesia.json"
if _forests_path.exists():
    try:
        _f_data = json.loads(_forests_path.read_text(encoding="utf-8-sig"))
        _f_list = _f_data if isinstance(_f_data, list) else _f_data.get("forests", [])
        for _f in _f_list:
            NATIONAL_KARHUTLA[_f["id"]] = {
                "event_id": _f["id"],
                "hazard": "fire",
                "name": _f["name"],
                "forest_type": _f.get("forest_type", "Kawasan Hutan"),
                "province": _f["province"],
                "coordinates": {"latitude": _f["lat"], "longitude": _f["lon"]}
            }
    except Exception:
        pass


@router.get("/events")
def list_events():
    events_list = []
    seen_ids = set()

    # 1. Muat event yang sudah memiliki direktori di data/events/
    if EVENTS_DIR.exists():
        for d in sorted(EVENTS_DIR.iterdir()):
            if d.is_dir():
                meta_file = d / "meta.json"
                if meta_file.exists():
                    try:
                        meta = json.loads(meta_file.read_text(encoding="utf-8-sig"))
                        eid = meta.get("event_id", d.name)
                        events_list.append({
                            "event_id": eid,
                            "hazard": meta.get("hazard"),
                            "name": meta.get("name"),
                            "start_utc": meta.get("start_utc"),
                            "end_utc": meta.get("end_utc"),
                            "members_source": meta.get("members_source"),
                            "n_members": meta.get("n_members"),
                            "data_status": meta.get("data_status"),
                        })
                        seen_ids.add(eid)
                    except Exception:
                        pass

    # 2. Tambahkan seluruh gunung api dari katalog 70 gunung api nasional
    try:
        from app.db.repositories.volcano_repo import VolcanoRepository
        db_volcs = VolcanoRepository.get_all()
        for v in db_volcs:
            eid = v.get("id") or v.get("event_id")
            if eid and eid not in seen_ids:
                events_list.append({
                    "event_id": eid,
                    "hazard": "volcano",
                    "name": f"[{v.get('level_name', 'Level I')}] {v.get('name')} ({v.get('province')})",
                    "region": v.get("region", "Indonesia"),
                    "elevation_m": v.get("elevation_m"),
                    "members_source": "open_meteo_live_forecast_api",
                    "n_members": 51,
                    "data_status": {"weather": "open_meteo_live_or_ensemble", "vona": "pvmbg_national_catalog"}
                })
                seen_ids.add(eid)
    except Exception:
        volc_path = BACKEND_DIR / "data" / "layers" / "volcanoes_indonesia.geojson"
        if volc_path.exists():
            try:
                geo = json.loads(volc_path.read_text(encoding="utf-8-sig"))
                for f in geo.get("features", []):
                    p = f.get("properties", {})
                    eid = p.get("id") or p.get("event_id")
                    if eid and eid not in seen_ids:
                        events_list.append({
                            "event_id": eid,
                            "hazard": "volcano",
                            "name": f"[{p.get('level_name', 'Level I')}] {p.get('name')} ({p.get('province')})",
                            "region": p.get("region", "Indonesia"),
                            "elevation_m": p.get("elevation_m"),
                            "members_source": "open_meteo_live_forecast_api",
                            "n_members": 51,
                            "data_status": {"weather": "open_meteo_live_or_ensemble", "vona": "pvmbg_national_catalog"}
                        })
                        seen_ids.add(eid)
            except Exception:
                pass

    # 3. Tambahkan seluruh zona karhutla nasional
    for eid, k in NATIONAL_KARHUTLA.items():
        if eid not in seen_ids:
            events_list.append({
                "event_id": eid,
                "hazard": "fire",
                "name": k["name"],
                "province": k["province"],
                "members_source": "open_meteo_live_forecast_api",
                "n_members": 51,
                "data_status": {"weather": "open_meteo_live_or_ensemble", "firms": "live_nrt_cluster"}
            })
            seen_ids.add(eid)

    return {"events": events_list}


@router.get("/events/{event_id}")
def get_event_detail(event_id: str):
    clean_id = (event_id or "").strip()
    if not clean_id:
        raise HTTPException(status_code=400, detail="ID event tidak boleh kosong.")
    event_id = clean_id
    meta_file = EVENTS_DIR / event_id / "meta.json"
    if meta_file.exists():
        return json.loads(meta_file.read_text(encoding="utf-8-sig"))

    # Cek direktori di data/events yang cocok (toleran terhadap perbedaan underscore)
    clean_eid = event_id.replace("_", "").lower()
    if EVENTS_DIR.exists():
        for d in EVENTS_DIR.iterdir():
            d_clean = d.name.replace("_", "").lower()
            if d.is_dir() and (d_clean == clean_eid or d_clean.startswith(clean_eid) or clean_eid in d_clean):
                mf = d / "meta.json"
                if mf.exists():
                    try:
                        return json.loads(mf.read_text(encoding="utf-8-sig"))
                    except Exception:
                        pass

    # Cari di katalog gunung api nasional
    volc_path = BACKEND_DIR / "data" / "layers" / "volcanoes_indonesia.geojson"
    if volc_path.exists():
        try:
            geo = json.loads(volc_path.read_text(encoding="utf-8-sig"))
            clean_e = event_id.replace("_", "").lower()
            for f in geo.get("features", []):
                p = f.get("properties", {})
                f_id = (p.get("id") or "").lower()
                f_ev = (p.get("event_id") or "").lower()
                clean_fid = f_id.replace("_", "")
                clean_fev = f_ev.replace("_", "")
                if clean_fid == clean_e or clean_fev == clean_e or clean_fid.startswith(clean_e) or clean_e in clean_fid:
                    c = f["geometry"]["coordinates"]
                    return {
                        "event_id": p.get("id"),
                        "hazard": "volcano",
                        "name": f"Erupsi {p.get('name')} ({p.get('province')})",
                        "elevation_m": p.get("elevation_m"),
                        "alert_level_at_event": p.get("level_name"),
                        "restricted_radius_km": p.get("radius_bahaya_km", 5.0),
                        "coordinates": {"latitude": c[1], "longitude": c[0]},
                        "source": "PVMBG Badan Geologi ESDM RI (Katalog 70 Gunung Api Nasional)"
                    }
        except Exception:
            pass

    # Cari di katalog karhutla nasional
    if event_id in NATIONAL_KARHUTLA:
        k = NATIONAL_KARHUTLA[event_id]
        return {
            "event_id": event_id,
            "hazard": "fire",
            "name": k["name"],
            "province": k["province"],
            "coordinates": k["coordinates"],
            "source": "NASA FIRMS NRT (Zona Karhutla Nasional)"
        }

    # Cari di katalog 36 kawasan hutan & konservasi nasional
    forest_path = BACKEND_DIR / "data" / "layers" / "forests_indonesia.json"
    if forest_path.exists():
        try:
            f_data = json.loads(forest_path.read_text(encoding="utf-8-sig"))
            f_list = f_data if isinstance(f_data, list) else f_data.get("forests", [])
            clean_e = event_id.replace("_", "").lower()
            for f_item in f_list:
                f_id = (f_item.get("id") or "").lower()
                clean_fid = f_id.replace("_", "")
                if clean_fid == clean_e or clean_fid.startswith(clean_e) or clean_e in clean_fid:
                    return {
                        "event_id": f_item.get("id"),
                        "hazard": "fire",
                        "name": f_item.get("name"),
                        "forest_type": f_item.get("forest_type"),
                        "province": f_item.get("province"),
                        "region": f_item.get("region"),
                        "risk_level": f_item.get("risk_level"),
                        "area_ha": f_item.get("area_ha"),
                        "coordinates": {"latitude": f_item.get("lat"), "longitude": f_item.get("lon")},
                        "source": "Katalog 36 Kawasan Hutan & Konservasi Nasional"
                    }
        except Exception:
            pass

    raise HTTPException(status_code=404, detail=f"Event '{event_id}' tidak ditemukan di katalog nasional.")
