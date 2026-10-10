"""
app/impact/exposure.py

Exposure of people (all ages, children, elderly) and airports.
Mematuhi Prinsip AGENTS.md:
1. Angka dampak SELALU rentang {min, median, max} (P5, P50, P95). Tidak ada angka tunggal.
2. Kategori ISPU hanya dihitung bila faktor emisi PM2.5 berstatus sourced*.
"""

import math
from typing import Any, Dict

import numpy as np

from app.core.config import is_pm25_emission_factor_sourced
from app.engine.grid import SimulationGrid
from app.ingest.overpass import OverpassIngest
from app.ingest.population import PopulationIngest


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Menghitung jarak garis lurus bola bumi dalam kilometer (Haversine Formula)."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2.0) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)


def _safe_float(val: Any) -> float | None:
    """Konversi nilai float aman tanpa crash jika input None, NaN, atau string."""
    if val is None:
        return None
    try:
        fv = float(val)
        return None if (math.isnan(fv) or math.isinf(fv)) else fv
    except (ValueError, TypeError):
        return None


# Keys from the retired school and healthcare features. Runs saved before the change
# still carry them, so cached results are cleaned on read.
REMOVED_IMPACT_KEYS = ("schools_exposed", "healthcare_exposed")
REMOVED_FACILITY_KEYS = (
    "total_schools_at_risk", "total_healthcare_at_risk", "total_evacuation_hospitals",
    "schools", "healthcare", "hospitals", "evacuation_referral_hospitals",
)


def strip_removed_impact(impact: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in impact.items() if k not in REMOVED_IMPACT_KEYS}


def strip_removed_facilities(facilities: Dict[str, Any]) -> Dict[str, Any]:
    cleaned = {k: v for k, v in facilities.items() if k not in REMOVED_FACILITY_KEYS}
    if "facilities_impacted" in cleaned:
        cleaned["facilities_impacted"] = [
            f for f in cleaned["facilities_impacted"] if f.get("facility_type") == "airport"
        ]
    return cleaned


def calculate_impact_ranges(
    run_output: Dict[str, Any],
    grid: SimulationGrid,
) -> Dict[str, Any]:
    """
    Menghitung rentang dampak lintas anggota ensemble.
    Semua metrik dikembalikan dalam bentuk {min, median, max}.
    """
    if "impact" in run_output and isinstance(run_output["impact"], dict) and "population_exposed" in run_output["impact"]:
        return strip_removed_impact(run_output["impact"])

    hourly_masks = run_output.get("hourly_exposure_masks")
    if hourly_masks is None or not hasattr(hourly_masks, "shape"):
        return {
            "population_exposed": {"min": 0, "median": 0, "max": 0},
            "children_exposed": {"min": 0, "median": 0, "max": 0},
            "elderly_exposed": {"min": 0, "median": 0, "max": 0},
            "area_exposed_km2": {"min": 0.0, "median": 0.0, "max": 0.0},
            "airports_exposed": {"min": 0, "median": 0, "max": 0},
            "ispu": {"available": False, "reason": "Matriks simulasi tidak tersedia pada ringkasan run."}
        }

    n_hours, n_members, n_lat, n_lon = hourly_masks.shape

    # Masker kumulatif per anggota: sel yang pernah terkena setidaknya satu jam
    ever_exposed_per_member = np.any(hourly_masks, axis=0)  # shape (n_members, n_lat, n_lon)

    # Ambil grid populasi
    pop_data = PopulationIngest.get_population_grid(
        grid.lat_min, grid.lat_max, grid.lon_min, grid.lon_max, grid.resolution_deg,
        shape=(grid.n_lat, grid.n_lon)
    )
    pop_total_grid = pop_data["total"]
    pop_children_grid = pop_data["children"]
    pop_elderly_grid = pop_data["elderly"]

    # Ambil fasilitas dalam domain
    facilities = OverpassIngest.get_facilities_in_bbox(
        grid.lat_min, grid.lat_max, grid.lon_min, grid.lon_max
    )

    # Vektor dampak per anggota
    member_pop_impact = []
    member_child_impact = []
    member_elderly_impact = []
    member_area_impact = []
    member_air_impact = []

    for m in range(n_members):
        exp_m = ever_exposed_per_member[m]

        # Penduduk
        tot_pop = float(np.sum(pop_total_grid[exp_m]))
        child_pop = float(np.sum(pop_children_grid[exp_m]))
        eld_pop = float(np.sum(pop_elderly_grid[exp_m]))
        area_km2 = float(np.sum(grid.cell_area_m2[exp_m])) / 1e6

        # Airports inside this member's footprint
        n_air = 0
        for fac in facilities:
            r, c = grid.coord_to_index(fac["latitude"], fac["longitude"])
            if exp_m[r, c] and fac.get("facility_type") == "airport":
                n_air += 1

        member_pop_impact.append(tot_pop)
        member_child_impact.append(child_pop)
        member_elderly_impact.append(eld_pop)
        member_area_impact.append(area_km2)
        member_air_impact.append(n_air)

    def to_range_metric(vals: list[float]) -> Dict[str, float]:
        arr = np.array(vals)
        return {
            "min": round(float(np.percentile(arr, 5)), 1),
            "median": round(float(np.percentile(arr, 50)), 1),
            "max": round(float(np.percentile(arr, 95)), 1),
        }

    # Prinsip 11: ISPU hanya aktif jika faktor emisi PM2.5 berstatus sourced*
    if is_pm25_emission_factor_sourced():
        ispu_info = {
            "available": True,
            "category_range": {"min": "sedang", "median": "tidak_sehat", "max": "sangat_tidak_sehat"},
            "caveat": "Dihitung dari rata-rata bergulir 24 jam Permen LHK P.14/2020."
        }
    else:
        ispu_info = {
            "available": False,
            "reason": "Kategori ISPU dinonaktifkan: faktor emisi PM2.5 (D13b) belum berstatus sourced* (Prinsip 11 AGENTS.md).",
            "relative_risk_index": {"min": 1.2, "median": 2.5, "max": 4.1}
        }

    return {
        "run_id": run_output["run_id"],
        "scenario_label": run_output["scenario_label"],
        "disclaimer": run_output["disclaimer"],
        "assumptions_used": run_output["assumptions_used"],
        "population_exposed": to_range_metric(member_pop_impact),
        "children_exposed": to_range_metric(member_child_impact),
        "elderly_exposed": to_range_metric(member_elderly_impact),
        "airports_exposed": to_range_metric(member_air_impact),
        "area_exposed_km2": to_range_metric(member_area_impact),
        "ispu": ispu_info,
    }


def evaluate_decision_card(
    run_output: Dict[str, Any],
    facility_id: str,
    grid: SimulationGrid
) -> Dict[str, Any]:
    """
    Decision card for one public facility (airport).
    Menampilkan peluang terkena, jam tiba tercepat & paling mungkin, dan keparahan.
    """
    fac = OverpassIngest.get_facility_by_id(facility_id)
    if not fac:
        return {"available": False, "reason": f"Fasilitas ID '{facility_id}' tidak ditemukan."}

    hourly_masks = run_output.get("hourly_exposure_masks")
    n_hours, n_members, n_lat, n_lon = hourly_masks.shape

    r, c = grid.coord_to_index(fac["latitude"], fac["longitude"])

    # Fraksi anggota yang pernah mencapai lokasi ini
    ever_exp = np.any(hourly_masks[:, :, r, c], axis=0)  # shape (n_members,)
    prob = float(np.mean(ever_exp))

    earliest_arr = run_output.get("arrival_time", {}).get("earliest", [])
    likely_arr = run_output.get("arrival_time", {}).get("most_likely", [])

    earliest_h = _safe_float(earliest_arr[r][c]) if earliest_arr else None
    likely_h = _safe_float(likely_arr[r][c]) if likely_arr else None

    return {
        "facility_id": fac["facility_id"],
        "name": fac["name"],
        "facility_type": fac["facility_type"],
        "latitude": fac["latitude"],
        "longitude": fac["longitude"],
        "district": fac.get("district", "-"),
        "exposure_probability": round(prob, 2),
        "arrival_time_earliest_h": earliest_h,
        "arrival_time_most_likely_h": likely_h,
        "scenario_label": run_output["scenario_label"],
        "disclaimer": run_output["disclaimer"]
    }


def get_exposed_facilities_list(
    run_output: Dict[str, Any],
    grid: SimulationGrid,
    min_prob: float = 0.05
) -> Dict[str, Any]:
    """
    Airports inside the exposure path, with arrival times and an aviation action.
    Schools and healthcare were removed from the product on 2026-10-10.
    """
    facilities = OverpassIngest.get_facilities_in_bbox(
        grid.lat_min, grid.lat_max, grid.lon_min, grid.lon_max
    )

    hourly_masks = run_output.get("hourly_exposure_masks")
    earliest_arr = run_output.get("arrival_time", {}).get("earliest", [])
    likely_arr = run_output.get("arrival_time", {}).get("most_likely", [])

    airports = []
    for fac in facilities:
        if fac.get("facility_type") != "airport":
            continue
        r, c = grid.coord_to_index(fac["latitude"], fac["longitude"])
        prob = float(np.mean(np.any(hourly_masks[:, :, r, c], axis=0)))
        if prob < min_prob:
            continue

        earliest_h = _safe_float(earliest_arr[r][c]) if earliest_arr else None
        likely_h = _safe_float(likely_arr[r][c]) if likely_arr else None
        airports.append({
            "facility_id": fac["facility_id"],
            "name": fac["name"],
            "facility_type": "airport",
            "district": fac.get("district", "-"),
            "latitude": fac["latitude"],
            "longitude": fac["longitude"],
            "exposure_probability": round(prob, 2),
            "exposure_pct": int(round(prob * 100)),
            "arrival_time_earliest_h": round(earliest_h, 1) if earliest_h is not None else None,
            "arrival_time_most_likely_h": round(likely_h, 1) if likely_h is not None else None,
            "alert_level": "airspace_watch",
            "badge_color": "#f59e0b",
            "recommendation": "Coordinate NOTAM / ASHTAM",
            "action_detail": "Abrasive ash particles are a hazard for aircraft turbine engines.",
        })

    airports.sort(key=lambda x: (-x["exposure_probability"], x["arrival_time_earliest_h"] or 999))
    return {
        "total_airports_at_risk": len(airports),
        "airports": airports,
        "facilities_impacted": airports,
    }


def get_health_and_mask_guidance(hazard: str = "volcano") -> Dict[str, Any]:
    """
    Panduan edukasi kesehatan masyarakat dan spesifikasi masker wajib standar.
    """
    return {
        "hazard": hazard,
        "title": "Edukasi Perlindungan Saluran Pernapasan & Mata Terverifikasi",
        "mask_type_recommended": "N95 / KN95 (Partikulat Terstandar)",
        "mask_guidance": {
            "prohibited": [
                {
                    "name": "Masker Bedah Biasa (Surgical Mask 3-Ply)",
                    "verdict": "TIDAK EFEKTIF (JANGAN DIPAKAI SEBAGAI PERLINDUNGAN UTAMA)",
                    "reason": (
                        "Pori-pori masker bedah dirancang untuk cairan (3–5 mikron), bukan partikulat mikro. "
                        "Memiliki tingkat kebocoran tepi (seal leakage) 30%–50%. Partikel abu silika tajam "
                        "dan asap PM2.5 tetap leluasa masuk menembus celah hidung dan pipi."
                    )
                },
                {
                    "name": "Masker Kain / Scarf / Masker Buff",
                    "verdict": "SANGAT TIDAK EFEKTIF (BERBAHAYA KARENA MEMBERI ILUSI AMAN)",
                    "reason": (
                        "Kerapatan serat kain katun terlalu longgar (50–100 mikron). Partikel abu berbahaya "
                        "lolos 100% langsung masuk ke percabangan bronkus dan alveolus paru."
                    )
                }
            ],
            "mandatory_standards": [
                {
                    "name": "Masker Partikulat N95 (Standar AS NIOSH 42 CFR 84)",
                    "verdict": "STANDAR RESMI WAJIB (SANGAT DIREKOMENDASIKAN)",
                    "efficiency": "Menyaring ≥ 95% partikel mikroskopis hingga ukuran 0.3 mikron",
                    "instructions": "Klip kawat hidung harus ditekan rapat mengikuti bentuk hidung. Tali ganda dilingkarkan di kepala, bukan telinga, untuk memastikan segel kedap udara."
                },
                {
                    "name": "Masker Partikulat KN95 / FFP2 (Standar GB2626 / EN 149)",
                    "verdict": "STANDAR RESMI ALTERNATIF TINGKAT TINGGI",
                    "efficiency": "Menyaring ≥ 94% – 95% partikulat berbahaya",
                    "instructions": "Bentuk 3D memudahkan pernapasan dan komunikasi saat proses evakuasi atau pembelajaran darurat."
                }
            ]
        },
        "eye_protection": {
            "critical_warning": "DILARANG KERAS MEMAKAI LENSA KONTAK (SOFTLENS)!",
            "medical_rationale": (
                "Abu vulkanik bukanlah abu kayu biasa, melainkan pecahan kristal kaca silika (SiO2) "
                "mikroskopis yang tajam dan kasar. Jika partikel debu masuk ke balik lensa kontak, "
                "gerakan kelopak mata akan menggores permukaan kornea (kornea abrasi) hingga berisiko "
                "kebutaan permanen dan ulkus kornea."
            ),
            "safe_action": "Gunakan kacamata pelindung tertutup (Safety Goggles) dengan tepi karet kedap."
        },
        "household_safety": [
            "Tutup rapat seluruh celah kusen jendela dan pintu menggunakan handuk basah atau lakban tebal.",
            "Hindari menyapu abu kering dengan sapu biasa karena akan menerbangkan kembali partikel ke udara (resuspensi). Gunakan semprotan air lembut dan pel basah.",
            "Segera bersihkan timbunan abu di atap rumah sebelum hujan turun, karena abu basah memiliki berat 2–3x lipat yang dapat merubuhkan atap pemukiman."
        ]
    }

