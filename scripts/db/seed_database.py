"""
scripts/db/seed_database.py

Skrip migrasi dan seeding database terpadu UdaraSiaga (SQLite + R*Tree).
Mengimpor seluruh katalog 70 Gunung Api PVMBG, 36 Kawasan Hutan & Lahan Gambut,
310 Fasilitas Publik Strategis Nasional, dan Hotspot Satelit FIRMS ke dalam udarasiaga.db.
"""

import csv
import json
import time
from pathlib import Path

# Setup path ke backend root
BACKEND_DIR = Path(__file__).resolve().parents[2]
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.schema import init_db_schema
from app.db.session import DB_PATH, get_db_connection
from app.db.repositories.facility_repo import FacilityRepository
from app.db.repositories.forest_repo import ForestRepository
from app.db.repositories.hotspot_repo import HotspotRepository
from app.db.repositories.volcano_repo import VolcanoRepository


def seed_all():
    print(f"🚀 Memulai migrasi & seeding database UdaraSiaga: {DB_PATH}")
    start_time = time.time()

    # 1. Inisialisasi skema dan R*Tree triggers
    conn = get_db_connection()
    init_db_schema(conn)
    conn.close()
    print("✅ Skema database & R*Tree triggers berhasil diinisialisasi.")

    # 2. Seeding 70 Gunung Api
    volcanoes_file = BACKEND_DIR / "data" / "layers" / "volcanoes_indonesia.geojson"
    if volcanoes_file.exists():
        with open(volcanoes_file, "r", encoding="utf-8-sig") as f:
            v_data = json.load(f)
        volcs_to_insert = []
        for feat in v_data.get("features", []):
            props = feat.get("properties", {})
            coords = feat.get("geometry", {}).get("coordinates", [0, 0])
            props["longitude"] = coords[0]
            props["latitude"] = coords[1]
            volcs_to_insert.append(props)

        n_v = VolcanoRepository.upsert_batch(volcs_to_insert)
        print(f"🌋 Berhasil mengimpor {n_v} Gunung Api PVMBG ke database.")
    else:
        print("⚠️ File volcanoes_indonesia.geojson tidak ditemukan.")

    # 3. Seeding 36 Kawasan Hutan & Poligon Spasial Batas
    forests_file = BACKEND_DIR / "data" / "layers" / "forests_indonesia.json"
    boundaries_file = BACKEND_DIR / "data" / "layers" / "forest_boundaries.geojson"

    boundaries_map = {}
    if boundaries_file.exists():
        with open(boundaries_file, "r", encoding="utf-8-sig") as f:
            b_data = json.load(f)
        for feat in b_data.get("features", []):
            fid = feat.get("id") or feat.get("properties", {}).get("id") or feat.get("properties", {}).get("forest_id")
            if fid:
                boundaries_map[fid] = feat.get("geometry")

    if forests_file.exists():
        with open(forests_file, "r", encoding="utf-8-sig") as f:
            forests_data = json.load(f)
        for f_item in forests_data:
            fid = f_item.get("id")
            if fid in boundaries_map:
                f_item["geometry"] = boundaries_map[fid]

        n_f = ForestRepository.upsert_batch(forests_data)
        print(f"🌲 Berhasil mengimpor {n_f} Kawasan Hutan & Gambut beserta poligon spasial.")
    else:
        print("⚠️ File forests_indonesia.json tidak ditemukan.")

    # 4. Seeding Fasilitas Publik (Sekolah, Faskes, Bandara)
    facilities_file = BACKEND_DIR / "data" / "layers" / "facilities_indonesia.json"
    if facilities_file.exists():
        with open(facilities_file, "r", encoding="utf-8-sig") as f:
            facs_data = json.load(f)
        n_fac = FacilityRepository.upsert_batch(facs_data)
        print(f"🏫 Berhasil mengimpor {n_fac} Fasilitas Publik Nasional (Sekolah, Faskes, Bandara).")
    else:
        print("⚠️ File facilities_indonesia.json tidak ditemukan.")

    # 5. Seeding Titik Api Satelit (Seluruh 36 Kawasan Hutan & Event Karhutla Nasional)
    hotspots_to_insert = []
    events_dir = BACKEND_DIR / "data" / "events"
    if events_dir.exists():
        for event_folder in sorted(events_dir.iterdir()):
            if not event_folder.is_dir():
                continue
            event_id = event_folder.name
            csv_path = event_folder / "hotspots.csv"
            if csv_path.exists():
                with open(csv_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            hotspots_to_insert.append({
                                "event_id": event_id,
                                "latitude": float(row["latitude"]),
                                "longitude": float(row["longitude"]),
                                "brightness": float(row.get("brightness", 320.0)),
                                "confidence": row.get("confidence", "nominal"),
                                "frp": float(row.get("frp", 15.0)),
                                "acq_date": row.get("acq_date", "2026-10-06")
                            })
                        except Exception:
                            continue

    if hotspots_to_insert:
        # Bersihkan dulu hotspots lama sebelum insert
        conn = get_db_connection()
        conn.execute("DELETE FROM hotspots;")
        conn.commit()
        conn.close()

        n_h = HotspotRepository.insert_batch(hotspots_to_insert)
        print(f"🔥 Berhasil mengimpor {n_h} Titik Api Satelit NASA FIRMS.")

    duration = time.time() - start_time
    print(f"✨ Seeding database selesai dalam {duration:.2f} detik! File: {DB_PATH}")


if __name__ == "__main__":
    seed_all()
