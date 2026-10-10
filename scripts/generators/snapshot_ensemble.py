"""
scripts/snapshot_ensemble.py

Mengambil snapshot anggota ensemble cuaca dari Open-Meteo Ensemble API.
Menyimpan ke data/events/{event_id}/weather_ensemble.json.
Dijalankan secara berkala (mis. tiap 6 jam) untuk event berjalan sebelum data anggota terhapus (retensi 3 hari).
Menghormati STANDBAI_OFFLINE=1.
"""

import argparse
import datetime
import json
import os
from pathlib import Path

import httpx

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = Path(__file__).resolve().parents[2]
EVENTS_DIR = BACKEND_DIR / "data" / "events"
USER_AGENT = "Standbai/1.0 (+https://github.com/ITHACKITS/BE-FORGEHACK-2026)"

PRESSURE_LEVELS = ["1000hPa", "850hPa", "700hPa", "500hPa", "250hPa", "100hPa", "50hPa"]
SURFACE_VARS = ["wind_speed_10m", "wind_direction_10m", "wind_speed_80m", "wind_speed_100m", "wind_speed_120m", "precipitation"]


def get_pressure_vars():
    vars_list = []
    for p in PRESSURE_LEVELS:
        vars_list.append(f"wind_speed_{p}")
        vars_list.append(f"wind_direction_{p}")
    vars_list.append("geopotential_height_1000hPa")
    vars_list.append("geopotential_height_500hPa")
    return vars_list


def fetch_ensemble_snapshot(
    event_id: str,
    lat: float,
    lon: float,
    models: str = "icon_seamless",
    forecast_days: int = 2,
    output_dir: Path | None = None
) -> dict:
    if output_dir is None:
        target_dir = EVENTS_DIR / event_id
    else:
        target_dir = Path(output_dir)

    target_dir.mkdir(parents=True, exist_ok=True)
    out_file = target_dir / "weather_ensemble.json"

    is_offline = os.environ.get("STANDBAI_OFFLINE") == "1"
    now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if is_offline:
        print("[OFFLINE] STANDBAI_OFFLINE=1 aktif. Snapshot dilewati atau memakai data tersimpan.")
        if out_file.exists():
            print(f"[OFFLINE] Memuat data cache yang ada di {out_file}")
            return json.loads(out_file.read_text(encoding="utf-8"))
        # Buat stub data offline
        stub = {
            "event_id": event_id,
            "created_at_utc": now_utc,
            "latitude": lat,
            "longitude": lon,
            "models": models,
            "members_source": "offline_synthetic_stub",
            "n_members": 51,
            "hourly": {
                "time": [f"2026-10-05T{h:02d}:00:00Z" for h in range(48)],
                "precipitation": [0.0] * 48,
                "wind_speed_10m": [5.0] * 48,
                "wind_direction_10m": [90.0] * 48,
            }
        }
        out_file.write_text(json.dumps(stub, indent=2), encoding="utf-8")
        return stub

    all_hourly_vars = SURFACE_VARS + get_pressure_vars()
    base_url = "https://ensemble-api.open-meteo.com/v1/ensemble"
    params = {
        "latitude": lat,
        "longitude": lon,
        "models": models,
        "hourly": ",".join(all_hourly_vars),
        "forecast_days": forecast_days,
    }

    print(f"Mengunduh ensemble dari Open-Meteo untuk {event_id} ({lat}, {lon}) model={models}...")
    with httpx.Client(timeout=30.0, headers={"User-Agent": USER_AGENT}) as client:
        resp = client.get(base_url, params=params)
        if resp.status_code != 200:
            raise RuntimeError(f"Open-Meteo error {resp.status_code}: {resp.text[:200]}")

        raw_data = resp.json()

    # Hitung jumlah anggota dari keys
    hourly = raw_data.get("hourly", {})
    member_keys = [k for k in hourly.keys() if "member" in k]
    members_set = set()
    for mk in member_keys:
        # e.g. wind_speed_10m_member01 -> member01
        parts = mk.split("_")
        for part in parts:
            if part.startswith("member"):
                members_set.add(part)

    n_members = len(members_set) if members_set else 1

    payload = {
        "event_id": event_id,
        "snapshot_at_utc": now_utc,
        "latitude": lat,
        "longitude": lon,
        "models": models,
        "forecast_days": forecast_days,
        "n_members": n_members,
        "members_source": "open_meteo_ensemble",
        "hourly_units": raw_data.get("hourly_units", {}),
        "hourly": hourly,
    }

    out_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Snapshot berhasil disimpan ke {out_file} ({n_members} anggota terdeteksi).")
    return payload


def main():
    parser = argparse.ArgumentParser(description="Snapshot Open-Meteo Ensemble members ke folder event.")
    parser.add_argument("--event", default="live_kalimantan", help="ID Event (default: live_kalimantan)")
    parser.add_argument("--lat", type=float, default=-2.5, help="Latitude")
    parser.add_argument("--lon", type=float, default=113.0, help="Longitude")
    parser.add_argument("--models", default="icon_seamless", help="Model ensemble (default: icon_seamless)")
    parser.add_argument("--days", type=int, default=2, help="Forecast days (default: 2)")
    parser.add_argument("--all", action="store_true", help="Snapshot semua event siap pakai")
    args = parser.parse_args()

    if args.all:
        events = [
            ("anak_krakatau_2026_09", -6.102, 105.423, "icon_seamless"),
            ("live_kalimantan", -2.5, 113.0, "icon_seamless"),
        ]
        for eid, lat, lon, mod in events:
            try:
                fetch_ensemble_snapshot(eid, lat, lon, models=mod, forecast_days=args.days)
            except Exception as e:
                print(f"Gagal snapshot {eid}: {e}")
    else:
        fetch_ensemble_snapshot(args.event, args.lat, args.lon, models=args.models, forecast_days=args.days)


if __name__ == "__main__":
    main()
