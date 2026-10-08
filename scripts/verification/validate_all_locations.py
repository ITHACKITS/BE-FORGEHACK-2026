"""
backend/scripts/verification/validate_all_locations.py
Validasi komprehensif seluruh lokasi simulasi gunung api dan kebakaran hutan.
Menggunakan FastAPI TestClient untuk pengujian mandiri & deterministik.
"""

import sys
import time
from pathlib import Path

# Setup path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def validate_event(event_id: str, hazard: str, label: str, custom_coords: dict = None):
    print(f"\n--- Menguji: [{hazard.upper()}] {label} ({event_id}) ---")
    payload = {
        "hazard": hazard,
        "n_members": 5,
        "seed": 42,
        "source": {
            "event_id": event_id
        }
    }
    if custom_coords:
        payload["source"]["latitude"] = custom_coords["latitude"]
        payload["source"]["longitude"] = custom_coords["longitude"]
        payload["source"]["name"] = custom_coords.get("name")
        payload["source"]["event_id"] = None

    # 1. POST /simulate
    t0 = time.time()
    res = client.post("/simulate", json=payload)
    if res.status_code != 200:
        print(f"  ❌ GAGAL POST /simulate: HTTP {res.status_code} - {res.text[:200]}")
        return False

    elapsed = time.time() - t0
    data = res.json()
    run_id = data.get("run_id")
    if not run_id:
        print(f"  ❌ run_id tidak ditemukan di respons")
        return False
    print(f"  ✅ Simulasi Berhasil dalam {elapsed:.2f}s | run_id={run_id}")

    # 2. GET /runs/{run_id}/tiers?t=12
    r_tiers = client.get(f"/runs/{run_id}/tiers?t=12")
    if r_tiers.status_code != 200:
        print(f"  ❌ GAGAL GET /runs/{run_id}/tiers: HTTP {r_tiers.status_code}")
        return False
    tiers_geo = r_tiers.json()
    feats = tiers_geo.get("features", [])
    tier_names = [f.get("properties", {}).get("tier") for f in feats]
    print(f"  ✅ Tiers GeoJSON (T=12): {len(feats)} fitur poligon ({', '.join(str(t) for t in tier_names)})")

    # 3. GET /runs/{run_id}/impact
    r_impact = client.get(f"/runs/{run_id}/impact")
    if r_impact.status_code != 200:
        print(f"  ❌ GAGAL GET /runs/{run_id}/impact: HTTP {r_impact.status_code}")
        return False
    impact = r_impact.json()
    pop = impact.get("population_exposed", {})
    sch = impact.get("schools_exposed", {})
    hl = impact.get("healthcare_exposed", {})
    area = impact.get("area_exposed_km2", {})
    print(f"  ✅ Metrik Dampak: Populasi={pop.get('median', 0):,} | Sekolah={sch.get('median', 0)} | Faskes={hl.get('median', 0)} | Area={area.get('median', 0):.1f} km²")

    # 4. GET /runs/{run_id}/facilities-impacted?min_prob=0.05
    r_facs = client.get(f"/runs/{run_id}/facilities-impacted?min_prob=0.05")
    if r_facs.status_code != 200:
        print(f"  ❌ GAGAL GET /runs/{run_id}/facilities-impacted: HTTP {r_facs.status_code}")
        return False
    facs = r_facs.json()
    schools = facs.get("schools", [])
    hospitals = facs.get("evacuation_referral_hospitals", [])

    for s in schools:
        pct = s.get("exposure_pct", 0)
        alert = s.get("alert_level")
        assert pct >= 5, f"Sekolah {s.get('name')} paparan < 5%: {pct}%"
        if pct >= 90:
            assert alert == "SIAGA TINGGI", f"Sekolah {s.get('name')} {pct}% harus SIAGA TINGGI, dapat {alert}"
        elif pct >= 50:
            assert alert == "WASPADA", f"Sekolah {s.get('name')} {pct}% harus WASPADA, dapat {alert}"
        else:
            assert alert == "SIAGA DINI", f"Sekolah {s.get('name')} {pct}% harus SIAGA DINI, dapat {alert}"

        safe_h = s.get("nearest_safe_hospital")
        if safe_h:
            assert safe_h.get("is_safe") is True, f"RS rujukan {safe_h.get('name')} harus is_safe=True"

    safe_count = sum(1 for h in hospitals if h.get("is_safe"))
    print(f"  ✅ Fasilitas Terdampak: {len(schools)} Sekolah (100% konsisten P90/P50/P05) & {len(hospitals)} RS Rujukan ({safe_count} RS Aman Bebas Paparan)")

    # 5. GET /runs/{run_id}/emergency-advisory
    r_adv = client.get(f"/runs/{run_id}/emergency-advisory")
    if r_adv.status_code != 200:
        print(f"  ❌ GAGAL GET /runs/{run_id}/emergency-advisory: HTTP {r_adv.status_code}")
        return False
    adv = r_adv.json()
    status = adv.get("status")
    rec_count = len(adv.get("general_recommendations", []))
    print(f"  ✅ Arahan Darurat: Status={status} | {rec_count} Rekomendasi Sektor")

    return True

def main():
    print("=" * 80)
    print("🔬 MEMULAI VALIDASI SELURUH LOKASI GUNUNG API & KEBAKARAN HUTAN (LIVE TESTCLIENT)")
    print("=" * 80)

    VOLCANO_TARGETS = [
        ("merapi_yogyakarta", "Gunung Merapi (DIY / Jateng)"),
        ("anak_krakatau_2026_09", "Anak Krakatau (Selat Sunda / Lampung / Banten)"),
        ("semeru", "Gunung Semeru (Lumajang, Jatim)"),
        ("sinabung", "Gunung Sinabung (Karo, Sumut)"),
        ("marapi_sumatera", "Gunung Marapi (Sumbar)"),
        ("bromo", "Gunung Bromo (Tengger, Jatim)"),
        ("kelud", "Gunung Kelud (Kediri, Jatim)"),
        ("agung", "Gunung Agung (Karangasem, Bali)"),
        ("rinjani", "Gunung Rinjani (Lombok, NTB)"),
        ("ruang", "Gunung Ruang (Tagulandang, Sulut)"),
        ("lewotobi_laki_laki", "Gunung Lewotobi Laki-laki (Flores Timur, NTT)"),
        ("ibu", "Gunung Ibu (Halmahera Barat, Malut)"),
        ("dukono", "Gunung Dukono (Halmahera Utara, Malut)"),
    ]

    FIRE_TARGETS = [
        ("karhutla_riau", "Karhutla Riau (Sumatera)"),
        ("karhutla_jambi", "Karhutla Jambi (Sumatera)"),
        ("karhutla_sumsel", "Karhutla Sumatera Selatan"),
        ("karhutla_kalbar", "Karhutla Kalimantan Barat"),
        ("karhutla_kalsel", "Karhutla Kalimantan Selatan"),
        ("hutan_way_kambas", "Taman Nasional Way Kambas (Lampung)"),
        ("hutan_bukit_tigapuluh", "Taman Nasional Bukit Tigapuluh (Riau/Jambi)"),
        ("hutan_tesso_nilo", "Taman Nasional Tesso Nilo (Pelalawan, Riau)"),
        ("hutan_sebangau", "Taman Nasional Sebangau (Kalteng)"),
        ("hutan_tanjung_puting", "Taman Nasional Tanjung Puting (Kobar, Kalteng)"),
        ("hutan_meratus", "Kawasan Pegunungan Meratus (Kalsel)"),
        ("hutan_kutai", "Taman Nasional Kutai (Kaltim)"),
        ("hutan_ciremai", "Taman Nasional Gunung Ciremai (Jabar)"),
        ("hutan_rinjani", "Kawasan Hutan Rinjani (NTB)"),
    ]

    CUSTOM_TARGETS = [
        ("custom_volc_bandung", "volcano", "Titik Gunung Kustom Tangkuban Perahu", {"latitude": -6.76, "longitude": 107.60, "name": "Kustom Tangkuban Perahu"}),
        ("custom_fire_pontianak", "fire", "Titik Karhutla Kustom Dekat Pontianak", {"latitude": -0.15, "longitude": 109.45, "name": "Kustom Lahan Gambut Pontianak"}),
    ]

    success_count = 0
    total_count = len(VOLCANO_TARGETS) + len(FIRE_TARGETS) + len(CUSTOM_TARGETS)

    print(f"\n🌋 1. VALIDASI {len(VOLCANO_TARGETS)} LOKASI GUNUNG API:")
    for eid, lbl in VOLCANO_TARGETS:
        ok = validate_event(eid, "volcano", lbl)
        if ok:
            success_count += 1

    print(f"\n🔥 2. VALIDASI {len(FIRE_TARGETS)} LOKASI KEBAKARAN HUTAN & LAHAN:")
    for eid, lbl in FIRE_TARGETS:
        ok = validate_event(eid, "fire", lbl)
        if ok:
            success_count += 1

    print(f"\n📍 3. VALIDASI {len(CUSTOM_TARGETS)} TITIK KUSTOM INTERAKTIF:")
    for eid, haz, lbl, coords in CUSTOM_TARGETS:
        ok = validate_event(eid, haz, lbl, custom_coords=coords)
        if ok:
            success_count += 1

    print("\n" + "=" * 80)
    print(f"📊 HASIL AKHIR: {success_count}/{total_count} Lokasi Lolos Validasi Penuh ({success_count/total_count*100:.1f}%)")
    print("=" * 80)

    if success_count == total_count:
        print("🎉 SELURUH SIMULASI DI SEMUA LOKASI GUNUNG API & KEBAKARAN 100% SUKSES DAN VALID!")
        sys.exit(0)
    else:
        print(f"⚠️ DITEMUKAN {total_count - success_count} LOKASI DENGAN MASALAH.")
        sys.exit(1)

if __name__ == "__main__":
    main()
