"""
scripts/github/populate_via_rest.py

Membuat 3 issue yang belum terbuat menggunakan REST API murni
(POST /repos/nyarikerja/JOINTS2026/issues), bukan GraphQL,
sehingga bebas dari batasan secondary rate limit GraphQL.
Kemudian mendaftarkannya ke Project 1.
"""

import json
import subprocess
import sys
import time

PROJECT_NUMBER = 1
PROJECT_OWNER = "nyarikerja"
REPO = "nyarikerja/JOINTS2026"
MILESTONE_NUMBER = 3  # Sprint 3 - Integrasi & QA
DUE_DATE = "2026-10-14"

ITEMS = [
    {
        "title": "Pitch Deck - Slide 12: Profil Tim Pengembang & Penutup CTA",
        "pic": "Anggota 1 (Lead Presenter)",
        "priority": "P0",
        "body": """### Alokasi: Slide 12 (0:45) | PIC: Anggota 1 (Lead Presenter)
**Framework:** Sequoia Team + Kawasaki Closing Call-to-Action  
**Tujuan:** Menutup presentasi dengan kesan profesionalisme tim yang solid dan pesan moral kemanusiaan yang berkesan mendalam.

**Pesan Inti:**  
Profil keahlian tim (Fisika Atmosfer/ML, Backend/Spasial, UX/GIS), ringkasan pesan moral, dan ajakan kolaborasi mewujudkan Indonesia Siaga Bencana.

**Elemen Visual Utama:**  
- Foto profil 3 anggota tim beserta keahlian kunci:
  - Lead / Atmospheric Physics & ML
  - Backend & Spatial Database Architect (SQLite R*Tree & OSRM)
  - Frontend & Product UX Engineer (Leaflet Tactical UI & 2-Tab Emas)
- **Call-to-Action Penutup:** *"Sains yang baik tidak boleh berhenti di jurnal. Sains yang baik harus menyelamatkan nyawa di daratan."*
- QR Code Repositori GitHub & Demo Aplikasi.
"""
    },
    {
        "title": "Pitch Deck - Appendix A1-A4: Slide Pertahanan Sesi Tanya Jawab (Q&A)",
        "pic": "Anggota 3 (Business & Q&A Defense Anchor)",
        "priority": "P0",
        "body": """### Alokasi: Appendix A1–A4 (Q&A Defense) | PIC: Anggota 3 (Business & Q&A Defense Anchor)
**Framework:** Appendix Defense Playbook  
**Tujuan:** Mempersiapkan slide cadangan teknis mendalam untuk menangkis pertanyaan kritis dewan juri pada sesi Q&A 5–8 menit.

**Rincian 4 Slide Lampiran:**
1. **Appendix A1: Formula MER Mastin 2009 & Evaluasi FSS**
   - Penjelasan turunan rumus Mastin: $M = 140.85 \\cdot H^{4.15}\\text{ kg/s}$ (above vent level).
   - Fraksi abu halus $m_{63} = 0.05$ (5% abu $<63\\ \\mu\\text{m}$).
   - Matriks Fractions Skill Score terhadap citra satelit Himawari.
2. **Appendix A2: Transparansi 24 Asumsi Ilmiah (D01–D24)**
   - Menunjukkan tabel katalog `config/assumptions.yaml` (Sourced, Secondary, Placeholder).
   - Penonaktifan etis kategori ISPU selama faktor emisi gambut belum primer.
3. **Appendix A3: Resiliensi Offline Guard (`UDARASIAGA_OFFLINE=1`)**
   - Bukti sistem tetap beroperasi 100% tanpa jaringan internet di workstation posko darurat.
4. **Appendix A4: Tata Kelola AI Tanpa Halusinasi (Strict Grounded Generation)**
   - Parameter fakta disuntikkan secara deterministik; suhu 0.2, larangan emoji total, dan fallback expert synthesizer lokal.
"""
    },
    {
        "title": "Pitch Deck - Checklist Juara & Simulasi Latihan Presentasi 11.5 Menit",
        "pic": "Semua",
        "priority": "P0",
        "body": """### Alokasi: Final Polish & Latihan | PIC: Semua
**Framework:** Checklist Juara JOINTS 2026  
**Tujuan:** Memastikan presentasi sempurna secara visual, teknis, dan tepat waktu dalam batas 11 menit 30 detik (safety buffer 30 detik).

**Daftar Periksa Akhir Sebelum Ekspor PDF:**
- [ ] **Rasio Aspek 16:9:** Resolusi standar layar lebar 1920x1080 px.
- [ ] **Aturan 3 Detik:** Pesan utama setiap slide dapat ditangkap dalam 3 detik pertama.
- [ ] **Nir-Dinding Teks (*No Wall of Text*):** Maksimal 25–30 kata per slide; prioritaskan kartu metrik dan diagram.
- [ ] **Palet Warna Taktis:** Latar `#0b0f19`, Aman `#10b981`, Waspada `#f59e0b`, Bahaya `#ef4444`, Intelejen `#38bdf8`.
- [ ] **Tipografi Modern:** Font sans-serif geometris (Inter/Outfit) dan font monospaced untuk koordinat telemetri.
- [ ] **Latihan Waktu Realistis:** Latihan berbicara dengan stopwatch minimal 3 kali hingga durasi stabil di **11 menit 15 detik s.d. 11 menit 30 detik**.
"""
    }
]

def main():
    for idx, item in enumerate(ITEMS, start=1):
        title = item["title"]
        body = item["body"]
        pic = item["pic"]
        priority = item["priority"]

        print(f"\n[{idx}/3] Membuat issue via REST: {title}", flush=True)
        # Gunakan gh api -X POST repos/nyarikerja/JOINTS2026/issues
        payload = {
            "title": title,
            "body": body,
            "milestone": MILESTONE_NUMBER,
            "labels": ["area:deck", priority]
        }
        res = subprocess.run(
            ["gh", "api", f"repos/{REPO}/issues", "-X", "POST", "--input", "-"],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        if res.returncode != 0:
            print(f"Gagal REST API: {res.stderr}", flush=True)
            continue

        issue_obj = json.loads(res.stdout)
        issue_url = issue_obj.get("html_url")
        print(f"  -> Berhasil dibuat: {issue_url}", flush=True)
        time.sleep(2)

        # Mendaftarkan ke Project 1
        print(f"  -> Menambahkan ke Project {PROJECT_NUMBER}...", flush=True)
        subprocess.run(["gh", "project", "item-add", str(PROJECT_NUMBER), "--owner", PROJECT_OWNER, "--url", issue_url], capture_output=True)
        time.sleep(2)

        # Set Project Fields
        for field, val in [("Status", "Todo"), ("Area", "Deck"), ("Priority", priority), ("Sprint", "Sprint 3")]:
            subprocess.run(["gh", "project", "item-edit", str(PROJECT_NUMBER), "--owner", PROJECT_OWNER, "--url", issue_url, "--field", field, "--value", val], capture_output=True)
            time.sleep(1)

        subprocess.run(["gh", "project", "item-edit", str(PROJECT_NUMBER), "--owner", PROJECT_OWNER, "--url", issue_url, "--field", "Due Date", "--date", DUE_DATE], capture_output=True)
        time.sleep(1)
        subprocess.run(["gh", "project", "item-edit", str(PROJECT_NUMBER), "--owner", PROJECT_OWNER, "--url", issue_url, "--field", "PIC", "--text", pic], capture_output=True)
        time.sleep(2)
        print(f"  -> Sukses isi kolom Project 1 untuk {title}!", flush=True)

if __name__ == "__main__":
    main()
