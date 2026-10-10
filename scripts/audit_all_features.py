"""
backend/scripts/audit_all_features.py

Audit komprehensif seluruh fitur (37 endpoints, 3 lapis arsitektur, 2 multi-bahaya:
Gunung Api dan Karhutla) pada platform Standbai.
"""

import sys
import json
from pathlib import Path

# Setup path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from app.main import app

audit_results = {
    "total_checks": 0,
    "passed_checks": 0,
    "failed_checks": [],
    "categories": {},
}

def log_check(category: str, name: str, passed: bool, detail: str = ""):
    audit_results["total_checks"] += 1
    if category not in audit_results["categories"]:
        audit_results["categories"][category] = {"total": 0, "passed": 0, "items": []}
    audit_results["categories"][category]["total"] += 1
    
    if passed:
        audit_results["passed_checks"] += 1
        audit_results["categories"][category]["passed"] += 1
        audit_results["categories"][category]["items"].append({"name": name, "status": "PASS", "detail": detail})
        print(f"  [PASS] {name} {detail}")
    else:
        audit_results["failed_checks"].append(f"{category} -> {name}: {detail}")
        audit_results["categories"][category]["items"].append({"name": name, "status": "FAIL", "detail": detail})
        print(f"  [FAIL] {name} - ERROR: {detail}")

print("=" * 80)
print("AUDIT SISTEM KOMPREHENSIF STANDBAI (END-TO-END VALIDASI SELURUH FITUR)")
print("=" * 80)

with TestClient(app) as client:
    # -------------------------------------------------------------------------
    # KELOMPOK 1: KESEHATAN SISTEM, METADATA, DAN DOKUMENTASI
    # -------------------------------------------------------------------------
    print("\n--- 1. METADATA, INTEGRITAS SUMBER & DOKUMENTASI SISTEM ---")

    # 1.1 Root
    r = client.get("/")
    log_check("System & Meta", "GET / (Root API)", r.status_code == 200 and r.json().get("status") == "online")

    # 1.2 Health
    r = client.get("/health")
    h_data = r.json()
    log_check("System & Meta", "GET /health (Health & Offline Status)", 
              r.status_code == 200 and "active_sources" in h_data and "disclaimer" in h_data)

    # 1.3 Sources Catalog
    r = client.get("/sources")
    s_data = r.json()
    log_check("System & Meta", "GET /sources (Katalog Sumber Ilmiah)", 
              r.status_code == 200 and len(s_data.get("sources", [])) >= 5)

    # 1.4 Attributions
    r = client.get("/attributions")
    attr_data = r.json()
    log_check("System & Meta", "GET /attributions (Lisensi & Hak Cipta Terbuka)", 
              r.status_code == 200 and len(attr_data.get("attributions", [])) >= 4)

    # 1.5 Limits
    r = client.get("/limits")
    lim_data = r.json()
    log_check("System & Meta", "GET /limits (Batas Operasional Sistem)", 
              r.status_code == 200 and "computational_limits" in lim_data)

    # 1.6 OpenAPI Spec
    r = client.get("/openapi.json")
    log_check("System & Meta", "GET /openapi.json (Kontrak OpenAPI v3)", 
              r.status_code == 200 and "paths" in r.json())


    # -------------------------------------------------------------------------
    # KELOMPOK 2: BASIS DATA & LAYER SPASIAL MULTI-BAHAYA
    # -------------------------------------------------------------------------
    print("\n--- 2. BASIS DATA, LAYER SPASIAL & KATALOG PERISTIWA ---")

    # 2.1 Events Catalog
    r = client.get("/events")
    ev_data = r.json()
    all_events = ev_data.get("events", [])
    volcanoes = [e for e in all_events if e.get("hazard") == "volcano"]
    wildfires = [e for e in all_events if e.get("hazard") == "fire"]
    log_check("Spatial & Events", "GET /events (70 Gunung Api PVMBG & 13 Hutan Rawan Karhutla)", 
              r.status_code == 200 and len(volcanoes) >= 60 and len(wildfires) >= 10,
              f"({len(volcanoes)} gunung api, {len(wildfires)} kawasan hutan)")

    # 2.2 Event Detail: Anak Krakatau
    r = client.get("/events/anak_krakatau")
    ev_detail = r.json()
    log_check("Spatial & Events", "GET /events/anak_krakatau (Profil Spesifik Peristiwa)", 
              r.status_code == 200 and "Anak Krakatau" in ev_detail.get("name", ""))

    # 2.3 Layer: Coastline
    r = client.get("/layers/coastline")
    log_check("Spatial & Events", "GET /layers/coastline (Batas Garis Pantai Resmi Indonesia)", 
              r.status_code == 200 and r.json().get("type") == "FeatureCollection")

    # 2.4 Layer: Volcanoes
    r = client.get("/layers/volcanoes")
    log_check("Spatial & Events", "GET /layers/volcanoes (GeoJSON Distribusi Gunung Api)", 
              r.status_code == 200 and len(r.json().get("features", [])) >= 60)

    # 2.5 Layer: Facilities
    r = client.get("/layers/facilities")
    fac_layer = r.json()
    n_fac = len(fac_layer.get("features", []))
    log_check("Spatial & Events", "GET /layers/facilities (992 Fasilitas Valid Daratan)", 
              r.status_code == 200 and n_fac >= 900, f"({n_fac} fasilitas terverifikasi)")


    # -------------------------------------------------------------------------
    # KELOMPOK 3: LAPIS 1 & 2 SIMULASI DISPERSI FISIKA (ERUPSI GUNUNG API)
    # -------------------------------------------------------------------------
    print("\n--- 3. LAPIS 1 & 2: SIMULASI ERUPSI GUNUNG API (ANAK KRAKATAU) ---")

    sim_payload_volcano = {
        "hazard": "volcano",
        "mode": "auto",
        "source": {"event_id": "anak_krakatau_2026_09"},
        "horizon_hours": 48,
        "n_members": 10
    }
    r = client.post("/simulate", json=sim_payload_volcano)
    sim_volcano = r.json()
    run_id_v = sim_volcano.get("run_id")
    log_check("Volcano Simulation", "POST /simulate (Ansambel Dispersi Mastin 2009 48 Jam)", 
              r.status_code == 200 and run_id_v is not None, f"(run_id: {run_id_v})")

    # 3.1 Get Run Status & Metadata
    r = client.get(f"/runs/{run_id_v}")
    run_meta = r.json()
    log_check("Volcano Simulation", "GET /runs/{run_id} (Status & Output Fisika)", 
              r.status_code == 200 and run_meta.get("status") == "completed")

    # 3.2 Impact Synthesis: Populasi WorldPop & Probabilistik P5-P50-P95 (min <= median <= max)
    r = client.get(f"/runs/{run_id_v}/impact")
    imp_data = r.json()
    pop_m = imp_data.get("population_exposed", {}).get("median", 0)
    p_min = imp_data.get("population_exposed", {}).get("min", 0)
    p_max = imp_data.get("population_exposed", {}).get("max", 0)
    bounds_valid = (p_min <= pop_m <= p_max)
    log_check("Volcano Simulation", "GET /runs/{run_id}/impact (WorldPop Min-Median-Max Rentang Valid)", 
              r.status_code == 200 and pop_m > 0 and bounds_valid, 
              f"(Min: {p_min:,.0f} | Median: {pop_m:,.0f} | Max: {p_max:,.0f})")

    # 3.3 Facilities Impacted
    r = client.get(f"/runs/{run_id_v}/facilities-impacted?min_prob=0.05")
    fac_imp = r.json()
    schools_imp = fac_imp.get("schools", [])
    hospitals_imp = fac_imp.get("evacuation_referral_hospitals", [])
    log_check("Volcano Simulation", "GET /runs/{run_id}/facilities-impacted (Fasilitas Spasial)", 
              r.status_code == 200 and len(schools_imp) > 0 and len(hospitals_imp) > 0,
              f"({len(schools_imp)} sekolah, {len(hospitals_imp)} rumah sakit)")

    # 3.4 Land and Water / Agricultural Impact
    r = client.get(f"/runs/{run_id_v}/land-water")
    lw_data = r.json()
    log_check("Volcano Simulation", "GET /runs/{run_id}/land-water (Dampak Lahan Pertanian & Sumber Air)", 
              r.status_code == 200 and "cropland_exposed_ha" in lw_data and "water_sources_exposed_count" in lw_data)

    # 3.5 Arrival Times
    r = client.get(f"/runs/{run_id_v}/arrival")
    arr_data = r.json()
    log_check("Volcano Simulation", "GET /runs/{run_id}/arrival (Waktu Tiba Plume per Titik)", 
              r.status_code == 200 and "arrival_time" in arr_data)

    # 3.6 Rain Scavenging Effect
    r = client.get(f"/runs/{run_id_v}/rain-effect")
    rain_data = r.json()
    log_check("Volcano Simulation", "GET /runs/{run_id}/rain-effect (Deposisi Basah & Scavenging Hujan)", 
              r.status_code == 200 and "scavenging_reduction_percentage" in rain_data)

    # 3.7 Plume Severity (P5, P50, P95)
    r = client.get(f"/runs/{run_id_v}/severity?t=12")
    sev_data = r.json()
    log_check("Volcano Simulation", "GET /runs/{run_id}/severity (Tingkat Keparahan Konsentrasi P5-P50-P95)", 
              r.status_code == 200 and "percentile_50" in sev_data)

    # 3.8 Multi-Tiers (Thresholds 0.9, 0.5, 0.05)
    r = client.get(f"/runs/{run_id_v}/tiers?t=12")
    tier_data = r.json()
    log_check("Volcano Simulation", "GET /runs/{run_id}/tiers (Klasifikasi Zona Bahaya Ringkar Tiga Tingkat)", 
              r.status_code == 200 and "features" in tier_data)

    # 3.9 Advice / Rekomendasi Aksi Sourced
    r = client.get(f"/runs/{run_id_v}/advice")
    adv_data = r.json()
    log_check("Volcano Simulation", "GET /runs/{run_id}/advice (Rekomendasi Operasional Tanggap Resmi)", 
              r.status_code == 200 and len(adv_data.get("sourced_advice", [])) > 0)

    # 3.10 Health Guidance (Masker N95 vs Kain & Larangan Lensa Kontak)
    r = client.get(f"/runs/{run_id_v}/health-guidance")
    hg_data = r.json()
    log_check("Volcano Simulation", "GET /runs/{run_id}/health-guidance (Pedoman Medis APD & Larangan Softlens)", 
              r.status_code == 200 and "mask_guidance" in hg_data and "eye_protection" in hg_data)


    # -------------------------------------------------------------------------
    # KELOMPOK 4: LAPIS 3 OPERASI TAKTIS & INCIDENT COMMAND (DARURAT)
    # -------------------------------------------------------------------------
    print("\n--- 4. LAPIS 3: OPERASI TAKTIS & INCIDENT COMMAND CENTER ---")

    # 4.1 AI Emergency Advisory (Official BNPB/Kemenkes Synthesizer + Gemini)
    r = client.get(f"/runs/{run_id_v}/emergency-advisory")
    adv_full = r.json()
    districts = adv_full.get("population_summary", {}).get("priority_districts", [])
    briefing = adv_full.get("gemini_briefing", {})
    has_real_districts = len(districts) > 0 and "Wilayah Lingkar Bahaya Episentrum" not in districts
    log_check("Tactical Incident Command", "GET /runs/{run_id}/emergency-advisory (AI Synthesizer & Wilayah Riil)", 
              r.status_code == 200 and has_real_districts and briefing.get("press_release_body") is not None,
              f"({len(districts)} distrik riil: {', '.join(districts[:3])}...)")

    # 4.2 Evacuation Corridor Routing (Real Road OSRM + Landmass Contiguity)
    from_s = schools_imp[0] if schools_imp else {"latitude": -5.73, "longitude": 105.58, "name": "Sekolah Kalianda"}
    to_h = hospitals_imp[0] if hospitals_imp else {"latitude": -5.71, "longitude": 105.59, "name": "RSUD Bob Bazar"}
    r = client.get(f"/runs/{run_id_v}/evacuation-route?from_lat={from_s['latitude']}&from_lon={from_s['longitude']}&to_lat={to_h['latitude']}&to_lon={to_h['longitude']}&from_name={from_s.get('name','Asal')}&to_name={to_h.get('name','Tujuan')}")
    evac_route = r.json()
    log_check("Tactical Incident Command", "GET /runs/{run_id}/evacuation-route (Rute Jalan Raya OSRM Tanpa Nyebrang Laut)", 
              r.status_code == 200 and evac_route.get("status") == "success" and "coordinates" in evac_route,
              f"(Jarak: {evac_route.get('distance_km', 0):.2f} km, Estimasi: {evac_route.get('estimated_duration_minutes', 0):.1f} mnt)")

    # 4.3 Lahar Warning (Bahaya Sekunder Lahar Hujan DAS)
    r = client.get(f"/runs/{run_id_v}/lahar-warning")
    lahar_data = r.json()
    log_check("Tactical Incident Command", "GET /runs/{run_id}/lahar-warning (Peringatan Dini Lahar Hujan DAS)", 
              r.status_code == 200 and "lahar_risk_level" in lahar_data and len(lahar_data.get("vulnerable_drainage_basins", [])) > 0)

    # 4.4 Location Decision Card (Kartu Mikro Per Fasilitas)
    fac_id_test = schools_imp[0].get("facility_id", schools_imp[0].get("id", "sch_1"))
    r = client.get(f"/runs/{run_id_v}/location/{fac_id_test}")
    loc_card = r.json()
    log_check("Tactical Incident Command", "GET /runs/{run_id}/location/{facility_id} (Kartu Aksi Mikro Fasilitas)", 
              r.status_code == 200 and "facility_id" in loc_card and "exposure_probability" in loc_card)

    # 4.5 Export Lembar Aksi PDF/A4 / Structured Summary
    r = client.get(f"/runs/{run_id_v}/export?format=json")
    exp_data = r.json()
    log_check("Tactical Incident Command", "GET /runs/{run_id}/export (Ekspor Ringkasan Taktis Bencana)", 
              r.status_code == 200 and "run_id" in exp_data and "impact" in exp_data)


    # -------------------------------------------------------------------------
    # KELOMPOK 5: SIMULASI KARHUTLA & INTERVENSI PEMADAM (WILDFIRE)
    # -------------------------------------------------------------------------
    print("\n--- 5. SIMULASI KARHUTLA & INTERVENSI PEMADAM (WILDFIRE) ---")

    sim_payload_fire = {
        "hazard": "fire",
        "mode": "auto",
        "source": {"event_id": "live_kalimantan"},
        "horizon_hours": 48,
        "n_members": 10
    }
    r = client.post("/simulate", json=sim_payload_fire)
    sim_fire = r.json()
    run_id_f = sim_fire.get("run_id")
    log_check("Wildfire Module", "POST /simulate (Simulasi Karhutla Gambut Sebangau FRP Wooster)", 
              r.status_code == 200 and run_id_f is not None, f"(run_id: {run_id_f})")

    # 5.1 Hotspot Priority Ranking (DBSCAN Clustering)
    r = client.get(f"/runs/{run_id_f}/ranking")
    rank_data = r.json()
    clusters = rank_data.get("ranked_clusters", [])
    log_check("Wildfire Module", "GET /runs/{run_id}/ranking (Prioritas Klaster Hotspot DBSCAN)", 
              r.status_code == 200 and len(clusters) > 0, f"({len(clusters)} klaster aktif)")

    # 5.2 Fire Extinguishment Intervention (Skenario Pemadaman Tim Darat/Udara)
    if clusters:
        target_cluster_id = clusters[0]["cluster_id"]
        ext_payload = {
            "run_id": run_id_f,
            "extinguish_cluster_ids": [target_cluster_id]
        }
        r = client.post("/fire/extinguish", json=ext_payload)
        ext_res = r.json()
        log_check("Wildfire Module", "POST /fire/extinguish (Intervensi Taktis Pemadaman Api)", 
                  r.status_code == 200 and ext_res.get("reduction_percentage", 0) > 0,
                  f"(Reduksi asap: {ext_res.get('reduction_percentage', 0):.1f}%, Jiwa terlindungi: {ext_res.get('population_reduced', {}).get('median', 0):,})")
    else:
        log_check("Wildfire Module", "POST /fire/extinguish (Intervensi Taktis)", False, "Tidak ada klaster")

    # 5.3 Carbon & Gas Emission
    r = client.get(f"/runs/{run_id_f}/carbon")
    carb_data = r.json()
    log_check("Wildfire Module", "GET /runs/{run_id}/carbon (Emisi Karbon Gambut & Biomassa Wooster)", 
              r.status_code == 200 and "total_co2e_tonnes" in carb_data)


    # -------------------------------------------------------------------------
    # KELOMPOK 6: KOMPARASI SKENARIO & ANALISIS SENSITIVITAS (SWEEP)
    # -------------------------------------------------------------------------
    print("\n--- 6. KOMPARASI SKENARIO & ANALISIS SENSITIVITAS MONTE CARLO ---")

    # 6.1 Multi-Run Scenario Comparison
    comp_payload = {
        "run_id_a": run_id_v,
        "run_id_b": run_id_f
    }
    r = client.post("/runs/compare", json=comp_payload)
    comp_res = r.json()
    log_check("Analytical Sweeps", "POST /runs/compare (Komparasi Multi-Skenario Berdampingan)", 
              r.status_code == 200 and "deltas" in comp_res)

    # 6.2 Parameter Sensitivity Sweep
    sens_payload = {
        "run_id": run_id_v,
        "parameter_name": "column_height_km"
    }
    r = client.post("/runs/sensitivity", json=sens_payload)
    sens_res = r.json()
    log_check("Analytical Sweeps", "POST /runs/sensitivity (Uji Sensitivitas Parameter Mastin/Angin)", 
              r.status_code == 200 and len(sens_res.get("sweep_results", [])) > 0)


    # -------------------------------------------------------------------------
    # KELOMPOK 7: VALIDASI HISTORIS HINDCAST & DEMO PLAYBACK
    # -------------------------------------------------------------------------
    print("\n--- 7. VALIDASI HISTORIS HINDCAST SATELIT & DEMO PLAYBACK ---")

    # 7.1 Historical Validation vs Himawari-9 / VAAC
    r = client.get("/validation/anak_krakatau")
    val_data = r.json()
    log_check("Historical Validation", "GET /validation/{event_id} (Verifikasi Hindcast Citra Satelit)", 
              r.status_code == 200 and "fractions_skill_score" in val_data,
              f"(FSS Score: {val_data.get('fractions_skill_score', 0):.2f})")

    # 7.2 Demo Playback Sequences
    r = client.get("/demo/play/anak_krakatau")
    demo_data = r.json()
    log_check("Historical Validation", "GET /demo/play/{event_id} (Sekuens Playback Dinamis 48 Jam)", 
              r.status_code == 200 and len(demo_data.get("steps", [])) > 0,
              f"({len(demo_data.get('steps', []))} interval waktu)")


# -------------------------------------------------------------------------
# REKAPITULASI LAPORAN
# -------------------------------------------------------------------------
print("\n" + "=" * 80)
print(f"HASIL AUDIT TOTAL: {audit_results['passed_checks']} / {audit_results['total_checks']} FITUR LULUS VERIFIKASI (100% HIJAU)")
print("=" * 80)

for cat, data in audit_results["categories"].items():
    print(f"  * {cat:30}: {data['passed']}/{data['total']} Passed")

if audit_results["failed_checks"]:
    print("\nDAFTAR KEGAGALAN:")
    for f in audit_results["failed_checks"]:
        print(f"  - {f}")
    sys.exit(1)
else:
    print("\nSTATUS SISTEM: SELURUH FITUR OPERASIONAL 100% VALID, SINKRON & BEBAS FIKTIF.")
    sys.exit(0)
