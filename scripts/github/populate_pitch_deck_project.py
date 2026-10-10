"""
scripts/github/populate_pitch_deck_project.py

Menambahkan seluruh pembagian Pitch Deck UdaraSiaga v2 dari:
docs/Pembagian_Pitch_Deck_UdaraSiaga_v2_ContohVisual.md
ke GitHub Project 'https://github.com/orgs/nyarikerja/projects/1'.
Semua kolom diisi otomatis (Status, Area, Priority, Sprint, Due Date, PIC)
KECUALI assignees (dibiarkan kosong sesuai instruksi user).
"""

import json
import subprocess
import sys
import time

PROJECT_NUMBER = 1
PROJECT_OWNER = "nyarikerja"
REPO = "nyarikerja/JOINTS2026"
MILESTONE = "Sprint 3 - Integrasi & QA"
DUE_DATE = "2026-10-14"

ITEMS = [
    {
        "title": "Pitch Deck - Slide 1: Hook & Judul (Sains Penyelamat Jiwa)",
        "pic": "Anggota 1 (Lead Presenter)",
        "priority": "P0",
        "time": "0:30",
        "framework": "Guy Kawasaki (Title Slide)",
        "body": """### Alokasi: Slide 1 (0:30) | PIC: Anggota 1 (Lead Presenter)
**Framework:** Guy Kawasaki (Title Slide)  
**Tujuan:** Menarik perhatian juri dalam 5 detik pertama dengan pernyataan misi kuat, profesional, dan relevan dengan tema Sustainability.

**Pesan Inti:**  
Satu platform intelejen atmosferik multi-bahaya untuk melindungi jutaan nafas anak sekolah dan memandu evakuasi medis darurat.

**Elemen Visual Utama:**  
- Latar belakang: Gelap taktis (`#0b0f19`) dengan siluet kontur dispersi partikel halus dan kilatan sensor satelit.
- Sisi Kiri: Logo resmi UdaraSiaga, lencana status hijau berkedip `SIAGA 24/7`, sub-judul *"Sistem Intelejen Sebaran Atmosfer Multi-Bahaya & Panduan Evakuasi Dini Berbasis Sains"*.
- Sisi Kanan: Ticker telemetri nasional: *"70 Gunung Api Terpantau | 36 Kawasan Hutan Konservasi | Resolusi Spasial 100m"*.

**Naskah Presenter:**  
> *"Selamat pagi Dewan Juri yang terhormat. Setiap kali gunung api erupsi atau kebakaran hutan gambut melanda, jutaan anak sekolah dan warga rentan menghirup udara beracun tanpa tahu kapan bahaya tiba di depan pintu mereka. Kami mempersembahkan **UdaraSiaga**: platform intelejen atmosferik terpadu yang mentransformasi miliaran data satelit mentah menjadi instruksi evakuasi taktis dan kebijakan sekolah otomatis demi menyelamatkan generasi masa depan Indonesia."*
"""
    },
    {
        "title": "Pitch Deck - Slide 2: The Crisis (Krisis Masalah SPAB, ISPA & Silika)",
        "pic": "Anggota 1 (Lead Presenter)",
        "priority": "P0",
        "time": "1:00",
        "framework": "Sequoia Problem + Sendai Framework",
        "body": """### Alokasi: Slide 2 (1:00) | PIC: Anggota 1 (Lead Presenter)
**Framework:** Sequoia Problem + Sendai Framework  
**Tujuan:** Menunjukkan bahwa masalah ini nyata, mendesak, berakar pada ketiadaan jembatan keputusan, dan menelan korban nyata di sektor kesehatan dan pendidikan.

**Pesan Inti:**  
Paradoks data bencana: data satelit melimpah, tetapi saat letusan/karhutla terjadi, kepala sekolah bingung kapan meliburkan siswa dan ambulans terjebak rute abu pekat.

**Elemen Visual Utama (3 Kolom Masalah Berlatar Merah Taktis):**  
1. **Krisis Pendidikan (SPAB Lumpuh):** 1.200+ sekolah terdampak abu/asap setiap musim bencana; kepala sekolah terlambat meliburkan siswa karena menunggu birokrasi.
2. **Krisis Rujukan Medis:** Korban sesak napas akut (ISPA) dievakuasi ke RS terdekat yang ternyata terkepung abu pekat.
3. **Misinformasi APD & Abrasi Kornea:** Warga memakai masker kain berpori longgar dan memakai lensa kontak saat hujan abu, memicu luka robek kornea permanen akibat kristal silika tajam ($SiO_2$).

**Data Kunci:** Peningkatan 300% kasus ISPA akut dalam 72 jam pertama akibat keterlambatan aksi preventif.
"""
    },
    {
        "title": "Pitch Deck - Slide 3: Why Now & The Critical Gap (Jurang Data ke Aksi)",
        "pic": "Anggota 1 (Lead Presenter)",
        "priority": "P0",
        "time": "0:45",
        "framework": "Sequoia 'Why Now'",
        "body": """### Alokasi: Slide 3 (0:45) | PIC: Anggota 1 (Lead Presenter)
**Framework:** Sequoia 'Why Now'  
**Tujuan:** Menjelaskan jurang teknologi (*the critical gap*) dan mengapa solusi saat ini belum memecahkan masalah operasional lapangan.

**Pesan Inti:**  
Ketiadaan jembatan operasional antara data mentah sains (VONA, FIRMS, BMKG) dengan keputusan taktis di tingkat kecamatan dan garda depan.

**Elemen Visual Utama:**  
- Diagram Alir "The Broken Pipeline": *Sumber Data Mentah* (VONA Magma, NASA FIRMS, Himawari) $\to$ **JURANG PEMISAH (THE GAP)** $\to$ *Garda Depan Lapangan* (Sekolah, Faskes, Warga).
- Teks Kunci: *"Data ada di awan, tetapi keputusan hilang di daratan."*
"""
    },
    {
        "title": "Pitch Deck - Slide 4: The Solution (Platform UdaraSiaga Terpadu)",
        "pic": "Anggota 1 (Lead Presenter)",
        "priority": "P0",
        "time": "1:00",
        "framework": "Y Combinator Solution",
        "body": """### Alokasi: Slide 4 (1:00) | PIC: Anggota 1 (Lead Presenter)
**Framework:** Y Combinator Solution  
**Tujuan:** Memperkenalkan UdaraSiaga sebagai solusi komprehensif (*One Engine, Dual Hazard, Unified Action*).

**Pesan Inti:**  
Satu platform, satu mesin dispersi fisika Lagrangian RK2, mengintegrasikan 70 gunung api dan 36 kawasan hutan nasional menjadi aksi dini terpadu.

**Elemen Visual Utama:**  
- Mockup UI Beresolusi Tinggi menampilkan Peta Taktis Gelap, poligon kontur multi-probabilitas P90/P50/P5, dan laci analitik aksi dini.
- 3 Pilar Solusi:
  1. **Satu Mesin Fisika (Lagrangian RK2):** Skala nasional 38 provinsi (gunung api & karhutla).
  2. **Hierarki Yurisdiksi Spasial:** Mengelompokkan dampak langsung per kecamatan.
  3. **Protokol Tanggap Multi-Sektor:** Otomatisasi PJJ Daring sekolah, triase faskes aman, dan edukasi APD Kemenkes.
"""
    },
    {
        "title": "Pitch Deck - Slide 5: Live Product Demo & Alur Komando 2-Tab Emas",
        "pic": "Anggota 2 (Technical & Demo Master)",
        "priority": "P0",
        "time": "1:30",
        "framework": "Double Diamond Design Process",
        "body": """### Alokasi: Slide 5 (1:30) | PIC: Anggota 2 (Technical & Demo Master)
**Framework:** Double Diamond Design Process  
**Tujuan:** Memperlihatkan keunggulan *Model 2-Tab Emas* secara nyata dan membuktikan bahwa platform berfungsi penuh (*working live software*).

**Pesan Inti:**  
Alur komando taktis 5 langkah: Skenario otomatis $\to$ Kontur ansambel P90/P50/P5 $\to$ Wadah hierarki kecamatan $\to$ Rute riil OSRM faskes aman $\to$ AI briefing BNPB & cetak A4.

**Elemen Visual Utama:**  
- Step-by-step UI Walkthrough menampilkan Model 2-Tab Emas:
  - Tab 1: Kecamatan sebagai wadah induk, daftar sekolah siaga PJJ daring.
  - OSRM Routing: Ambulans menyusuri jalan raya riil berbelok (bukan garis lurus) ke RS rujukan bebas abu.
  - Tab 2: AI Emergency Briefing resmi BNPB tanpa emoji, 1-klik salin WhatsApp warga, dan tombol ekspor PDF Lembar Rencana Aksi Darurat format A4.
"""
    },
    {
        "title": "Pitch Deck - Slide 6: Underlying Magic & Arsitektur Sistem C4",
        "pic": "Anggota 2 (Technical & Demo Master)",
        "priority": "P0",
        "time": "1:30",
        "framework": "C4 Model + Kawasaki Magic",
        "body": """### Alokasi: Slide 6 (1:30) | PIC: Anggota 2 (Technical & Demo Master)
**Framework:** C4 Model (Container & Component) + Kawasaki Magic  
**Tujuan:** Membuktikan keunggulan rekayasa perangkat lunak (*software engineering excellence*) di hadapan juri teknis.

**Pesan Inti:**  
Arsitektur data berkinerja tinggi: Ingest satelit, database SQLite spasial R*Tree (<1 ms), integrasi OSRM real-road, dan Google Gemini AI dengan fallback deterministik lokal.

**Elemen Visual Utama:**  
- Diagram Arsitektur C4:
  - *Ingestion Layer:* Open-Meteo Ensemble API (1000–50 hPa), NASA FIRMS VIIRS SNPP, OpenAQ v3, PVMBG MAGMA.
  - *Storage & Indexing:* SQLite R*Tree Spatial Database (<1 ms query tanpa server eksternal boros daya).
  - *Simulation Core:* Lagrangian Particle Dispersion (adveksi RK2, difusi turbulen, wet scavenging).
  - *Routing & AI:* OSRM real road network & Google Gemini AI + BNPB deterministic fallback.
  - *Offline Guard:* `UDARASIAGA_OFFLINE=1` menjamin posko beroperasi saat internet bencana putus.
"""
    },
    {
        "title": "Pitch Deck - Slide 7: Integritas Sains & Validasi Ilmiah Mastin 2009",
        "pic": "Anggota 2 (Technical & Demo Master)",
        "priority": "P0",
        "time": "1:00",
        "framework": "NASA TRL (TRL 6) + Validasi FSS",
        "body": """### Alokasi: Slide 7 (1:00) | PIC: Anggota 2 (Technical & Demo Master)
**Framework:** NASA Technology Readiness Levels (TRL 6) + Validasi FSS  
**Tujuan:** Membangun kredibilitas akademis dan membedakan UdaraSiaga dari aplikasi visualisasi fiktif.

**Pesan Inti:**  
Kejujuran sains: Rentang ketidakpastian P5–P50–P95, formula empiris Mastin et al. 2009, validasi spasial FSS Letusan Krakatau 2026, dan transparansi etika penonaktifan ISPU.

**Elemen Visual Utama:**  
- **Formula Mastin et al. 2009:** $\dot{M} = 140.85 \cdot H^{4.15}\text{ kg/s}$ di atas bibir kawah (*above vent level*).
- **Kurva Dispersi Ansambel P5–P50–P95:** Rentang probabilistik jujur, bukan angka tunggal palsu.
- **Validasi Historis FSS:** Fractions Skill Score terhadap data satelit Himawari pada erupsi Anak Krakatau & Merapi.
- **Katalog 24 Asumsi Terbuka:** Transparansi status parameter (Sourced, Secondary, Placeholder) dari `config/assumptions.yaml`.
"""
    },
    {
        "title": "Pitch Deck - Slide 8: Multi-Sectoral Impact & Kontribusi 5 SDGs",
        "pic": "Anggota 1 (Lead Presenter)",
        "priority": "P0",
        "time": "1:00",
        "framework": "Theory of Change + UN SDGs",
        "body": """### Alokasi: Slide 8 (1:00) | PIC: Anggota 1 (Lead Presenter)
**Framework:** Theory of Change + UN SDGs  
**Tujuan:** Menunjukkan dampak kuantitatif terhadap pembangunan berkelanjutan (Sustainability, Healthcare, Education).

**Pesan Inti:**  
Kuantifikasi dampak riil: Intervensi pemadaman titik api pangkas 41% paparan, pengamanan sekolah ke PJJ, kontribusi nyata terhadap SDG 3, 4, 11, 13, dan 15.

**Elemen Visual Utama:**  
- Matriks 4 Sektor dengan Ikon Resmi PBB:
  - **SDG 3 (Health):** Spesifikasi respirator N95/KF94 & larangan softlens mencegah cedera kornea dan lonjakan ISPA.
  - **SDG 4 (Education):** Kerangka SPAB mengalihkan murid ke PJJ Daring tepat waktu.
  - **SDG 11 (Sustainable Cities):** Rute evakuasi jalan raya riil ke RS penyangga bebas abu.
  - **SDG 13 & 15 (Climate & Life on Land):** Intervensi pemadaman prioritas satgas udara pangkas 41% paparan dan cegah pelepasan tonase gas rumah kaca ($CO_2e$) dari kubah gambut.
"""
    },
    {
        "title": "Pitch Deck - Slide 9: Pengguna, Kelayakan, & Rencana Pilot Daerah",
        "pic": "Anggota 1 (Lead Presenter)",
        "priority": "P0",
        "time": "1:00",
        "framework": "Lean Canvas + Pilot Roadmap",
        "body": """### Alokasi: Slide 9 (1:00) | PIC: Anggota 1 (Lead Presenter)
**Framework:** Lean Canvas + Pilot Implementation Roadmap  
**Tujuan:** Menjelaskan siapa yang mengoperasikan sistem, bagaimana implementasinya di birokrasi daerah, dan kelayakan anggarannya.

**Pesan Inti:**  
Rencana adopsi praktis bersama BPBD, Disdik, dan Dinkes. Biaya operasional rendah, kemampuan offline 100% saat jaringan bencana lumpuh.

**Elemen Visual Utama:**  
- **Skema Pemangku Kepentingan 3 Tingkat:**
  - Tingkat 1 (Pusat Komando): Pusdalops BPBD & Dinas Kesehatan.
  - Tingkat 2 (Pelaksana Teknis): Kepala Satuan Pendidikan & Direktur RS (SPGDT 119).
  - Tingkat 3 (Masyarakat): Warga rentan via buletin WhatsApp terverifikasi.
- **Peta Jalan Pilot:** Kab. Lampung Selatan (Anak Krakatau) & Kab. Sleman (Merapi).
- **Efisiensi Anggaran:** Arsitektur nir-daemon berbasis SQLite lokal berbiaya mendekati nol rupiah.
"""
    },
    {
        "title": "Pitch Deck - Slide 10: Diferensiasi & Matriks Kompetitif 2x2",
        "pic": "Anggota 3 (Business & Q&A Defense Anchor)",
        "priority": "P1",
        "time": "0:45",
        "framework": "Kawasaki Competitive Matrix (2x2)",
        "body": """### Alokasi: Slide 10 (0:45) | PIC: Anggota 3 (Business & Q&A Defense Anchor)
**Framework:** Kawasaki Competitive Matrix (2x2 Matrix)  
**Tujuan:** Menegaskan posisi keunggulan UdaraSiaga dibanding platform pemantau yang sudah ada.

**Pesan Inti:**  
UdaraSiaga vs VONA Magma vs NASA FIRMS vs Aplikasi Cuaca Komersial. Kami bukan sekadar penampil titik, melainkan pengambil keputusan taktis.

**Elemen Visual Utama:**  
- **Kuadran 2x2:**
  - Sumbu X: Data Mentah Pasif $\to$ Pengambilan Keputusan Aksi Dini Taktis
  - Sumbu Y: Bahaya Tunggal Terisolasi $\to$ Multi-Bahaya Spasial Terpadu
- **Posisi Platform:**
  - Magma PVMBG: Kiri Atas (Hanya erupsi, format buletin penerbangan).
  - NASA FIRMS: Kiri Bawah (Hanya titik api pasif).
  - Aplikasi Cuaca Umum (Windy): Tengah Kiri (Angin makro umum).
  - **UdaraSiaga: Kanan Atas (Juara Kuadran): Multi-bahaya, satu mesin fisika, langsung menjadi keputusan taktis sekolah & medis.**
"""
    },
    {
        "title": "Pitch Deck - Slide 11: Roadmap Pengembangan & Mitigasi Risiko",
        "pic": "Anggota 3 (Business & Q&A Defense Anchor)",
        "priority": "P1",
        "time": "0:45",
        "framework": "YC Traction & Execution Plan",
        "body": """### Alokasi: Slide 11 (0:45) | PIC: Anggota 3 (Business & Q&A Defense Anchor)
**Framework:** YC Traction & Execution Plan  
**Tujuan:** Menunjukkan visi produk jangka panjang dan kehati-hatian dalam mengelola risiko teknis.

**Pesan Inti:**  
Roadmap 3 fase: Now (TRL 6 Prototype), Next (Sensor IoT & LoRa), Later (InaRISK BNPB). Mitigasi risiko internet padam & kepanikan publik.

**Elemen Visual Utama:**  
- **Timeline Roadmap 3 Fase:**
  - *Now (Q4 2026):* Prototype Lapis 1–3 tuntas, validasi FSS, OSRM & Gemini AI tanpa emoji, cetak A4 resmi.
  - *Next (Q1–Q2 2027):* SPKU IoT bergerak, transmisi radio darurat LoRa untuk blank spot.
  - *Later (Q3–Q4 2027):* Integrasi API ke InaRISK BNPB dan Satu Data Indonesia.
- **Tabel Mitigasi Risiko:**
  - Internet lumpuh $\to$ Offline guard SQLite R*Tree lokal.
  - Kepanikan publik $\to$ Label tegas skenario simulasi & narasi resmi Pusdalops BNPB.
"""
    },
    {
        "title": "Pitch Deck - Slide 12: Profil Tim Pengembang & Penutup CTA",
        "pic": "Anggota 1 (Lead Presenter)",
        "priority": "P0",
        "time": "0:45",
        "framework": "Sequoia Team + Kawasaki CTA",
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
        "time": "5:00 - 8:00 (Q&A)",
        "framework": "Appendix Defense Playbook",
        "body": """### Alokasi: Appendix A1–A4 (Q&A Defense) | PIC: Anggota 3 (Business & Q&A Defense Anchor)
**Framework:** Appendix Defense Playbook  
**Tujuan:** Mempersiapkan slide cadangan teknis mendalam untuk menangkis pertanyaan kritis dewan juri pada sesi Q&A 5–8 menit.

**Rincian 4 Slide Lampiran:**
1. **Appendix A1: Formula MER Mastin 2009 & Evaluasi FSS**
   - Penjelasan turunan rumus Mastin: $M = 140.85 \cdot H^{4.15}\text{ kg/s}$ (above vent level).
   - Fraksi abu halus $m_{63} = 0.05$ (5% abu $<63\ \mu\text{m}$).
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
        "time": "Latihan 3x (Target 11:30)",
        "framework": "Checklist Juara JOINTS 2026",
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

def run_cmd(cmd_list):
    res = subprocess.run(cmd_list, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        print(f"Error executing {' '.join(cmd_list)}:\n{res.stderr}")
    return res

def main():
    print(f"Memulai pembuatan {len(ITEMS)} issues Pitch Deck dan pendaftaran ke GitHub Project {PROJECT_NUMBER}...")

    # Cek issue yang sudah ada agar tidak duplikat
    list_res = run_cmd(["gh", "issue", "list", "--repo", REPO, "--label", "area:deck", "--limit", "100", "--json", "title,number,url"])
    existing_issues = {}
    if list_res.returncode == 0 and list_res.stdout.strip():
        try:
            for item in json.loads(list_res.stdout):
                existing_issues[item["title"].strip()] = item
        except Exception:
            pass

    for idx, item in enumerate(ITEMS, start=1):
        title = item["title"]
        body = item["body"]
        pic = item["pic"]
        priority = item["priority"]

        print(f"\n[{idx}/{len(ITEMS)}] Memproses: {title}")

        issue_url = None
        if title in existing_issues:
            issue_url = existing_issues[title]["url"]
            print(f"  -> Issue sudah ada: #{existing_issues[title]['number']} ({issue_url})")
        else:
            # Buat issue baru
            create_cmd = [
                "gh", "issue", "create",
                "--repo", REPO,
                "--title", title,
                "--body", body,
                "--label", "area:deck",
                "--label", priority,
                "--milestone", MILESTONE
            ]
            res = run_cmd(create_cmd)
            if res.returncode == 0:
                issue_url = res.stdout.strip()
                print(f"  -> Issue berhasil dibuat: {issue_url}")
            else:
                print(f"  -> Gagal buat issue: {res.stderr}")
                continue

        if not issue_url:
            continue

        # Tambahkan issue ke GitHub Project 1
        print(f"  -> Mendaftarkan ke Project {PROJECT_NUMBER}...")
        add_res = run_cmd([
            "gh", "project", "item-add", str(PROJECT_NUMBER),
            "--owner", PROJECT_OWNER,
            "--url", issue_url
        ])
        if add_res.returncode != 0:
            print(f"  -> Warning item-add: {add_res.stderr}")

        # Isi kolom-kolom project
        # 1. Status: Todo
        run_cmd([
            "gh", "project", "item-edit", str(PROJECT_NUMBER),
            "--owner", PROJECT_OWNER,
            "--url", issue_url,
            "--field", "Status",
            "--value", "Todo"
        ])

        # 2. Area: Deck
        run_cmd([
            "gh", "project", "item-edit", str(PROJECT_NUMBER),
            "--owner", PROJECT_OWNER,
            "--url", issue_url,
            "--field", "Area",
            "--value", "Deck"
        ])

        # 3. Priority: P0 / P1
        run_cmd([
            "gh", "project", "item-edit", str(PROJECT_NUMBER),
            "--owner", PROJECT_OWNER,
            "--url", issue_url,
            "--field", "Priority",
            "--value", priority
        ])

        # 4. Sprint: Sprint 3
        run_cmd([
            "gh", "project", "item-edit", str(PROJECT_NUMBER),
            "--owner", PROJECT_OWNER,
            "--url", issue_url,
            "--field", "Sprint",
            "--value", "Sprint 3"
        ])

        # 5. Due Date: 2026-10-14
        run_cmd([
            "gh", "project", "item-edit", str(PROJECT_NUMBER),
            "--owner", PROJECT_OWNER,
            "--url", issue_url,
            "--field", "Due Date",
            "--date", DUE_DATE
        ])

        # 6. PIC: Text
        run_cmd([
            "gh", "project", "item-edit", str(PROJECT_NUMBER),
            "--owner", PROJECT_OWNER,
            "--url", issue_url,
            "--field", "PIC",
            "--text", pic
        ])

        print(f"  -> Sukses memperbarui seluruh kolom (Status=Todo, Area=Deck, Priority={priority}, Sprint=Sprint 3, Due Date={DUE_DATE}, PIC={pic})")
        time.sleep(0.5)

    print("\nSeluruh 14 item Pitch Deck berhasil ditambahkan dan disinkronkan ke GitHub Project!")

if __name__ == "__main__":
    main()
