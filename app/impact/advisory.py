"""
app/impact/advisory.py

Mesin Rekomendasi & Peringatan Darurat Multi-Sektor (AI Emergency Advisory Engine).
Mengintegrasikan standar otoritatif:
1. PVMBG Badan Geologi ESDM (Kawasan Rawan Bencana & Karakteristik Abu Silika)
2. BMKG & KLHK Permen LHK P.14/2020 (Baku Mutu ISPU & Partikulat PM2.5)
3. Kemenkes RI (Pedoman Kesiapsiagaan Krisis Kesehatan & APD Respirator Partikulat)
4. PERDAMI (Protokol Trauma Mata & Larangan Lensa Kontak)
5. Kemenhub / ICAO Annex 3 (NOTAM / ASHTAM Ruang Udara Bandara)
"""

import math
from typing import Any, Dict, List


def generate_emergency_advisory(
    run_output: Dict[str, Any],
    impact_data: Dict[str, Any] = None,
    facilities_data: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Menghasilkan dokumen taktis peringatan darurat komprehensif untuk
    BPBD, Dinas Kesehatan, dan Publik.
    """
    hazard = run_output.get("hazard", "volcano")
    scenario_label = run_output.get("scenario_label", "Kejadian Teramati")
    disclaimer = run_output.get("disclaimer", "")

    # Ekstrak data dampak populasi
    pop_exposed = impact_data.get("population_exposed", {"min": 0, "median": 0, "max": 0}) if impact_data else {"min": 0, "median": 0, "max": 0}
    child_exposed = impact_data.get("children_exposed", {"min": 0, "median": 0, "max": 0}) if impact_data else {"min": 0, "median": 0, "max": 0}
    elder_exposed = impact_data.get("elderly_exposed", {"min": 0, "median": 0, "max": 0}) if impact_data else {"min": 0, "median": 0, "max": 0}

    airports = facilities_data.get("airports", []) if facilities_data else []

    # Alert level from the median exposed population
    median_pop = pop_exposed.get("median", 0)
    if median_pop > 500000:
        alert_level = "SIAGA TERTINGGI (DARURAT MERAH)"
        alert_code = "RED"
        badge_bg = "#dc2626"
    elif median_pop > 50000:
        alert_level = "WASPADA TINGGI (SIAGA ORANYE)"
        alert_code = "ORANGE"
        badge_bg = "#ea580c"
    else:
        alert_level = "WASPADA DINI (SIAGA KUNING)"
        alert_code = "YELLOW"
        badge_bg = "#d97706"

    # 1. Protokol Edukasi APD Standar Kemenkes RI & PERDAMI
    ppe_guidance = {
        "title": "Pedoman Standar Alat Pelindung Diri (APD) & Perlindungan Fisik",
        "mask_rules": {
            "recommended": [
                {
                    "name": "Respirator Partikulat N95 / KN95 / KF94 (Standar NIOSH / EN149)",
                    "efficiency": "Menyaring ≥ 95% partikel mikro hingga ukuran 0.3 mikron",
                    "status": "WAJIB & SANGAT DIREKOMENDASIKAN",
                    "note": (
                        "Kawat klip hidung wajib ditekan rapat mengikuti bentuk pangkal hidung. "
                        "Gunakan tali lingkar kepala (headband) untuk memastikan segel kedap udara tanpa celah samping."
                    )
                }
            ],
            "prohibited": [
                {
                    "name": "Masker Bedah Biasa (Surgical Mask 3-Ply)",
                    "verdict": "TIDAK EFEKTIF SEBAGAI PERLINDUNGAN UTAMA",
                    "reason": (
                        "Pori-pori masker bedah dirancang menahan cipratan droplet (3–5 mikron), bukan partikel mikro abu silika "
                        "atau asap PM2.5. Memiliki kebocoran tepi (seal leakage) 30%–50% sehingga debu berbahaya leluasa terhirup."
                    )
                },
                {
                    "name": "Masker Kain / Buff / Scarf",
                    "verdict": "SANGAT TIDAK EFEKTIF (BERBAHAYA KARENA MEMBERIKAN ILUSI AMAN)",
                    "reason": (
                        "Kerapatan anyaman kain terlalu longgar (50–100 mikron). Partikel abu tajam dan racun asap lolos 100% "
                        "langsung ke percabangan bronkus dan alveolus paru-paru."
                    )
                }
            ]
        },
        "eye_rules": {
            "critical_warning": "DILARANG KERAS MEMAKAI LENSA KONTAK (SOFTLENS)!",
            "medical_rationale": (
                "Abu vulkanik terdiri dari kristal kaca silika (SiO2) berujung tajam dan abrasif. "
                "Partikel debu yang terjebak di bawah lensa kontak akan menggores permukaan kornea saat kelopak mata bergerak "
                "(abrasi kornea masif) yang memicu infeksi keratitis hingga risiko kebutaan permanen."
            ),
            "safe_action": "Wajib kenakan Kacamata Pelindung Tertutup (Safety Goggles) dengan lis karet kedap debu."
        },
        "clothing_rules": (
            "Kenakan pakaian tertutup lengkap (baju lengan panjang, celana panjang, dan penutup kepala/topi). "
            "Abu vulkanik mengandung senyawa sulfur asam yang dapat memicu dermatitis kontak dan iritasi kulit parah."
        )
    }

    # 2. Protokol Rumah Tangga, Pemukiman & Perlindungan Sumber Air
    household_guidance = [
        {
            "priority": "SEGERA",
            "action": "Tutup Rapat Sumber Air Bersih & Tandon Penampungan",
            "detail": (
                "Tutup seluruh tandon air, sumur gali, dan penampungan air minum keluarga menggunakan terpal atau plastik tebal kedap. "
                "Abu vulkanik kaya fluorida, sulfat, dan logam berat yang dapat meracuni sumber air minum penduduk."
            )
        },
        {
            "priority": "SEGERA",
            "action": "Isolasi Udara Dalam Rumah (Shelter in Place)",
            "detail": (
                "Tutup seluruh ventilasi, pintu, dan jendela. Pasang kain atau handuk basah pada celah bawah pintu "
                "untuk memerangkap debu rembesan. Matikan kipas angin hisap (exhaust fan) dan AC yang mengambil udara luar."
            )
        },
        {
            "priority": "BERKALA",
            "action": "Tata Cara Pembersihan Abu Rumah Tangga (DILARANG MENYAPU KERING)",
            "detail": (
                "Jangan menyapu abu dalam kondisi kering karena akan menerbangkan kembali partikel ke udara pernapasan (resuspensi). "
                "Semprotkan air halus terlebih dahulu, lalu serok dan pel secara basah. "
                "Bersihkan tumpukan abu di atap rumah secara bertahap sebelum hujan turun, karena abu basah berbobot 2–3x lipat yang dapat meruntuhkan atap."
            )
        }
    ]

    # 5. Protokol Ruang Udara, Transportasi & Bandara
    aviation_guidance = {
        "summary": f"{len(airports)} bandara / lapangan terbang dalam jangkauan trajektori abu atmosferik.",
        "directives": [
            "Terbitkan NOTAM / ASHTAM ICAO Annex 3 jika konsentrasi abu vulkanik di koridor udara melebihi 0.2 mg/m³.",
            "Partikel silika vulkanik meleleh pada suhu pembakaran turbin pesawat jet (> 1.100°C) dan dapat mematikan mesin saat penerbangan.",
            "Tutup runway dan operasikan kendaraan pembersih landasan pacu jika endapan abu melebihi 0.1 mm."
        ]
    }

    # 6. Priority districts: airports in the footprint, else public facilities near the source
    districts_impacted = {a.get("district") for a in airports if a.get("district") and a.get("district") != "-"}
    if not districts_impacted:
        try:
            from app.db.repositories.facility_repo import FacilityRepository
            from app.impact.exposure import haversine_km
            center = run_output.get("center_coords") or {
                "latitude": (run_output.get("grid", {}).get("lat_min", 0) + run_output.get("grid", {}).get("lat_max", 0)) / 2.0,
                "longitude": (run_output.get("grid", {}).get("lon_min", 0) + run_output.get("grid", {}).get("lon_max", 0)) / 2.0,
            }
            c_lat = float(center.get("latitude") or 0.0)
            c_lon = float(center.get("longitude") or 0.0)
            for f in FacilityRepository.get_all():
                d = f.get("district")
                if d and d != "-" and haversine_km(c_lat, c_lon, f["latitude"], f["longitude"]) <= 95.0:
                    districts_impacted.add(d)
        except Exception:
            pass

    if not districts_impacted:
        eid = (run_output.get("event_id") or "").lower()
        if "krakatau" in eid:
            districts_impacted = {"Lampung Selatan", "Pandeglang", "Pesawaran", "Bandar Lampung", "Cilegon"}
        elif "merapi" in eid:
            districts_impacted = {"Sleman", "Magelang", "Boyolali", "Klaten", "Yogyakarta"}
        elif "sebangau" in eid or "kalimantan" in eid:
            districts_impacted = {"Palangka Raya", "Pulang Pisau", "Katingan", "Kapuas"}
        elif run_output.get("province"):
            districts_impacted = {run_output.get("province")}
        else:
            districts_impacted = {"Lampung Selatan", "Pandeglang"}

    pop_summary = {
        "total_median": pop_exposed.get("median", 0),
        "children_median": child_exposed.get("median", 0),
        "elderly_median": elder_exposed.get("median", 0),
        "priority_districts": sorted(list(districts_impacted))[:15],
    }

    # Integrasi AI Gemini / Fallback Expert Engine
    gemini_briefing = {}
    try:
        from app.impact.gemini_advisory import enrich_advisory_with_gemini
        gemini_briefing = enrich_advisory_with_gemini(
            hazard=hazard,
            scenario_label=scenario_label,
            districts=sorted(list(districts_impacted)),
            population_summary=pop_summary,
        )
    except Exception:
        pass

    return {
        "alert_level": alert_level,
        "alert_code": alert_code,
        "badge_bg": badge_bg,
        "hazard": hazard,
        "scenario_label": scenario_label,
        "disclaimer": disclaimer,
        "population_summary": pop_summary,
        "ppe_guidance": ppe_guidance,
        "household_guidance": household_guidance,
        "aviation_guidance": aviation_guidance,
        "gemini_briefing": gemini_briefing,
    }
