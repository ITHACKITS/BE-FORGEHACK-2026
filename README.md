# 🛡️ UdaraSiaga Backend API Gateway & Command Center — ITHACKITS FORGEHACK 2026

**Repository Resmi: FastAPI Core API Gateway, Disaster Database, OSRM Emergency Routing & Multi-Sectoral Impact Assessment**

Repository ini merupakan server backend utama (*Backend Service*) untuk platform komando tanggap darurat bencana atmosfer UdaraSiaga Indonesia. Menyediakan endpoint berkinerja tinggi untuk orkestrator simulasi, distribusi layer spasial GeoJSON nasional, rute evakuasi medis darurat OSRM, triase SPAB daring, dan ekspor laporan resmi.

---

## ⚡ Fitur Utama Backend

1. **REST API Gateway Terintegrasi (FastAPI)**
   - 37+ endpoint operasional dengan validasi skema ketat berbasis Pydantic v2.
   - Swagger / OpenAPI UI interaktif untuk pengujian langsung.
2. **Mesin Rute Evakuasi Medis Bebas Abu (OSRM Engine)**
   - Algoritma pencarian rute terpendek ambulans menuju rumah sakit rujukan aman di luar koridor dispersi partikulat.
   - Verifikasi kontiguitas daratan darat-ke-darat dan snapping jalan raya nasional.
3. **Penyimpanan Geospasial & Basis Data Kejadian**
   - SQLite relasional terindeks untuk persistensi status simulasi, log audit, dan metadata kejadian multi-bahaya.
   - Manajemen layer geospasial: Garis pantai nasional (13KB), 20+ gunung api aktif, 36 kawasan hutan konservasi, dan 990+ fasilitas publik.
4. **Analisis Dampak Multisektoral & Triase SPAB**
   - Estimasi populasi terpapar rentang realistis P5 / P50 / P95 (balita, lansia, masyarakat umum).
   - Triase Pembelajaran Jarak Jauh (PJJ Daring) sekolah berdasarkan ambang batas konsentrasi PM2.5/silika.
   - Deteksi ancaman lahar hujan pada badan air dan lahan pertanian daratan.
5. **Ekspor Dokumen & Pelaporan Multi-Format**
   - Ekspor ringkasan taktis format PDF, CSV, dan GeoJSON poligon probabilitas sebaran.

---

## 🚀 Panduan Memulai Cepat (Quickstart)

### 1. Prasyarat Sistem
- Python >= 3.10 / 3.11 / 3.12
- pip & virtualenv

### 2. Instalasi Dependensi
```bash
pip install -r requirements.txt
```

### 3. Konfigurasi Environment
```bash
cp .env.example .env
```

### 4. Menjalankan Server Backend
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Aplikasi backend aktif di **http://127.0.0.1:8000**.
Akses dokumentasi interaktif API di **http://127.0.0.1:8000/docs**.

### 5. Menjalankan Pengujian Otomatis
```bash
pytest tests -v
```
Seluruh 40 unit dan integrasi tes terverifikasi **100% lulus (40 passed)**.

---

## 📁 Struktur Direktori

```text
BE-FORGEHACK-2026/
├── app/
│   ├── api/                # Router endpoint FastAPI
│   │   ├── simulate.py     # Endpoint orkestrasi simulasi dispersi
│   │   ├── events.py       # CRUD & metadata kejadian multi-hazard
│   │   ├── layers.py       # Distribusi GeoJSON layer nasional
│   │   ├── lapis2.py       # Triase sekolah, RS rujukan, dampak multisektoral
│   │   ├── lapis3.py       # Rekomendasi darurat, ekspor PDF/CSV, analisis komparatif
│   │   ├── attributions.py # Integritas sumber data BMKG, PVMBG, NASA
│   │   └── health.py       # Healthcheck & offline status
│   ├── core/               # Konfigurasi aplikasi, offline guards, RNG
│   ├── db/                 # Skema SQLite, koneksi sesi, repository fasilitas
│   ├── engine/             # Engine komputasi terintegrasi & landmasking
│   ├── impact/             # OSRM routing, ekspor laporan, validasi sains
│   ├── ingest/             # Adapter data eksternal (Open-Meteo, FIRMS, Overpass)
│   ├── schemas/            # Pydantic request/response models
│   └── main.py             # Entry point FastAPI
├── data/
│   ├── layers/             # Data spasial GeoJSON daratan & fasilitas
│   ├── events/             # Skenario historis & observasi lapangan
│   └── udarasiaga.db       # Basis data SQLite
├── docs/                   # Spesifikasi API Contract & Arsitektur Database
├── scripts/                # Skrip audit end-to-end & utility tools
├── tests/                  # 40 pengujian terotomatisasi (pytest)
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## 🔗 Keterhubungan Komponen ForgeHack 2026

- **Frontend Command Center:** [FE-FORGEHACK-2026](https://github.com/ITHACKITS/FE-FORGEHACK-2026)
- **AI & Physics Dispersion Engine:** [AI-FORGEHACK-2026](https://github.com/ITHACKITS/AI-FORGEHACK-2026)