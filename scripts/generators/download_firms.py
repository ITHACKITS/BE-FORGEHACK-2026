"""
scripts/download_firms.py

Mengunduh data titik api dan FRP dari NASA FIRMS Area API.
Format: CSV saja, DAY_RANGE 1 sampai 5 hari per kueri.
Menggabungkan VIIRS dan MODIS, menghapus duplikat, menyimpan CSV.
Menghormati batas 5.000 transaksi per 10 menit.
Kunci MAP_KEY HANYA dari .env atau environment, tidak pernah dicetak di log.
Menghormati UDARASIAGA_OFFLINE=1.
"""

import argparse
import datetime
import os
import time
from pathlib import Path

import httpx

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = Path(__file__).resolve().parents[2]
EVENTS_DIR = BACKEND_DIR / "data" / "events"
USER_AGENT = "UdaraSiaga-FIRMSDownloader/1.0 (JOINTS2026 UGM Hackathon)"

# Load .env
ENV_FILE = BACKEND_DIR / ".env"
ENV_VARS = {}
if ENV_FILE.exists():
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            ENV_VARS[k.strip()] = v.strip().strip("'\"")

MAP_KEY = os.environ.get("FIRMS_MAP_KEY") or ENV_VARS.get("FIRMS_MAP_KEY")

CSV_HEADER = "latitude,longitude,brightness,scan,track,acq_date,acq_time,satellite,instrument,confidence,version,bright_t31,frp,daynight"

# Sample dummy hotspots untuk keperluan offline demo bila MAP_KEY belum diisi
OFFLINE_SAMPLE_HOTSPOTS = """latitude,longitude,brightness,scan,track,acq_date,acq_time,satellite,instrument,confidence,version,bright_t31,frp,daynight
-2.215,113.882,335.2,0.4,0.4,2026-10-04,0530,N,VIIRS,nominal,2.0NRT,298.5,42.5,D
-2.228,113.895,348.6,0.4,0.4,2026-10-04,0530,N,VIIRS,high,2.0NRT,301.2,78.2,D
-2.241,113.910,328.0,0.4,0.4,2026-10-04,0530,N,VIIRS,nominal,2.0NRT,295.1,28.4,D
-2.310,114.020,355.4,0.4,0.4,2026-10-04,0530,N,VIIRS,high,2.0NRT,305.0,95.1,D
-2.325,114.035,322.1,0.4,0.4,2026-10-04,0530,N,VIIRS,nominal,2.0NRT,293.4,19.8,D
-1.980,113.550,339.0,0.4,0.4,2026-10-04,0530,N,VIIRS,nominal,2.0NRT,299.0,51.3,D
-1.995,113.565,344.2,0.4,0.4,2026-10-04,0530,N,VIIRS,high,2.0NRT,300.5,67.0,D
-2.850,114.210,331.5,0.4,0.4,2026-10-04,0530,N,VIIRS,nominal,2.0NRT,297.8,36.2,D
-2.865,114.225,362.0,0.4,0.4,2026-10-04,0530,N,VIIRS,high,2.0NRT,308.2,112.4,D
-2.880,114.240,325.0,0.4,0.4,2026-10-04,0530,N,VIIRS,nominal,2.0NRT,294.0,22.0,D
"""


def parse_bbox_str(bbox_str: str) -> tuple[float, float, float, float]:
    parts = [float(p.strip()) for p in bbox_str.split(",")]
    if len(parts) != 4:
        raise ValueError("bbox harus berupa 4 angka: west,south,east,north")
    return parts[0], parts[1], parts[2], parts[3]


def download_firms_chunk(
    client: httpx.Client,
    map_key: str,
    source: str,
    west: float,
    south: float,
    east: float,
    north: float,
    day_range: int,
    date_str: str
) -> list[str]:
    # URL format: /api/area/csv/{MAP_KEY}/{SOURCE}/{west,south,east,north}/{DAY_RANGE}/{DATE}
    bbox_fmt = f"{west},{south},{east},{north}"
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{map_key}/{source}/{bbox_fmt}/{day_range}/{date_str}"

    resp = client.get(url)
    if resp.status_code != 200:
        print(f"[FIRMS] Warning: status code {resp.status_code} untuk {source} {date_str}")
        return []

    lines = resp.text.strip().splitlines()
    if not lines or "invalid" in lines[0].lower():
        print("[FIRMS] Warning: respons tidak valid atau map key bermasalah.")
        return []

    # Baris pertama biasanya header
    return lines[1:] if len(lines) > 1 else []


def download_hotspots(
    bbox: tuple[float, float, float, float],
    days: int = 3,
    end_date: str | None = None,
    output_path: Path | None = None,
    sources: list[str] | None = None
) -> Path:
    if output_path is None:
        output_path = EVENTS_DIR / "live_kalimantan" / "hotspots.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    is_offline = os.environ.get("UDARASIAGA_OFFLINE") == "1"

    if is_offline or not MAP_KEY:
        reason = "UDARASIAGA_OFFLINE=1 aktif" if is_offline else "FIRMS_MAP_KEY tidak ditemukan di .env"
        print(f"[FIRMS] {reason}. Menggunakan dataset offline / cache.")
        if output_path.exists() and output_path.stat().st_size > 0:
            print(f"[FIRMS] Mempertahankan data yang sudah ada di {output_path}")
            return output_path
        output_path.write_text(OFFLINE_SAMPLE_HOTSPOTS.strip() + "\n", encoding="utf-8")
        print(f"[FIRMS] Data contoh offline berhasil disimpan ke {output_path}")
        return output_path

    if sources is None:
        # Sumber resmi yang didukung FIRMS
        sources = ["VIIRS_SNPP_NRT", "MODIS_NRT"]

    if end_date is None:
        end_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    west, south, east, north = bbox

    # Pecah rentang hari ke potongan maksimal 5 hari (aturan FIRMS)
    remaining_days = days
    curr_end_dt = end_dt
    collected_rows = []

    with httpx.Client(timeout=30.0, headers={"User-Agent": USER_AGENT}) as client:
        while remaining_days > 0:
            chunk_days = min(remaining_days, 5)
            date_str = curr_end_dt.strftime("%Y-%m-%d")

            for src in sources:
                print(f"[FIRMS] Mengunduh {src} ({chunk_days} hari sampai {date_str})...")
                rows = download_firms_chunk(
                    client=client,
                    map_key=MAP_KEY,
                    source=src,
                    west=west,
                    south=south,
                    east=east,
                    north=north,
                    day_range=chunk_days,
                    date_str=date_str
                )
                collected_rows.extend(rows)
                time.sleep(0.5)  # Sopan terhadap rate limit

            remaining_days -= chunk_days
            curr_end_dt = curr_end_dt - datetime.timedelta(days=chunk_days)

    # Hapus duplikat titik api berdasarkan koordinat dan waktu
    unique_rows = {}
    for r in collected_rows:
        parts = r.split(",")
        if len(parts) >= 7:
            # key: lat, lon, acq_date, acq_time
            key = (parts[0], parts[1], parts[5], parts[6])
            unique_rows[key] = r

    final_csv_lines = [CSV_HEADER] + list(unique_rows.values())
    output_path.write_text("\n".join(final_csv_lines) + "\n", encoding="utf-8")
    print(f"[FIRMS] Selesai. {len(unique_rows)} titik api unik tersimpan di {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Download NASA FIRMS hotspots CSV")
    parser.add_argument("--bbox", default="110.0,-4.0,116.0,1.0", help="west,south,east,north")
    parser.add_argument("--days", type=int, default=3, help="Jumlah hari ke belakang (default: 3)")
    parser.add_argument("--end-date", default=None, help="Tanggal akhir YYYY-MM-DD (default: hari ini UTC)")
    parser.add_argument("--out", default=None, help="Path output CSV")
    args = parser.parse_args()

    bbox = parse_bbox_str(args.bbox)
    out_path = Path(args.out) if args.out else None
    download_hotspots(bbox=bbox, days=args.days, end_date=args.end_date, output_path=out_path)


if __name__ == "__main__":
    main()
