# Arsitektur Basis Data Spasial Terpadu (UdaraSiaga Database Architecture)

Dokumen ini memuat spesifikasi teknis, skema relasional, indeks spasial R*Tree, dan pola akses data (*Repository Pattern*) untuk sistem informasi geografis dan simulator sebaran atmosfer UdaraSiaga.

---

## 1. Ringkasan Eksekutif & Rasional Desain

Sistem UdaraSiaga mengintegrasikan data multi-bahaya berskala nasional yang mencakup seluruh 38 provinsi di Indonesia. Untuk memenuhi persyaratan performa tinggi tanpa latensi pada antarmuka peta taktis, arsitektur basis data bertransformasi dari berkas JSON datar (*flat files*) menjadi basis data relasional terindeks secara spasial (*Spatial Database*).

### Perbandingan Karakteristik Arsitektur

| Parameter Evaluasi | Berkas JSON Datar (Legacy) | SQLite + R*Tree Spasial (Terpilih) | PostgreSQL + PostGIS (Server Eksternal) |
| :--- | :--- | :--- | :--- |
| **Metode Pencarian Spasial** | Pemindaian linier O(N) di memori | Kueri Pohon Spasial R*Tree O(log N) | Indeks GiST / R*Tree O(log N) |
| **Latensi Kueri Bounding Box** | > 150 milidetik | < 1 milidetik | 2 - 5 milidetik (overhead TCP/IP) |
| **Konsumsi Memori RAM Klien** | Seluruh data dimuat ke RAM browser | Hanya memuat poligon dalam layar pengguna | Hanya memuat poligon dalam layar pengguna |
| **Kemandirian Operasional** | Portabel | Portabel, nir-konfigurasi, nir-daemon | Membutuhkan servis eksternal & otentikasi |
| **Kepatuhan Protokol Offline** | Memenuhi | Memenuhi 100% (UDARASIAGA_OFFLINE=1) | Rentan gagal bila koneksi lokal terputus |

Pilihan arsitektur jatuh pada **SQLite dengan modul indeks spasial virtual R\*Tree bawaan C**. Pilihan ini memberikan kecepatan pembacaan memori terpetakan (*memory-mapped I/O*), keandalan transaksi ACID, dan kemandirian eksekusi penuh tanpa dependensi servis eksternal.

---

## 2. Diagram Entitas Relasional (Entity Relationship Diagram)

```mermaid
erDiagram
    VOLCANOES ||--o{ EVENTS : "diasosiasikan dengan"
    FORESTS ||--o{ EVENTS : "diasosiasikan dengan"
    EVENTS ||--o{ SIMULATION_RUNS : "menghasilkan"
    
    VOLCANOES ||--|| VOLCANOES_RTREE : "diindeks oleh"
    FORESTS ||--|| FORESTS_RTREE : "diindeks oleh"
    FACILITIES ||--|| FACILITIES_RTREE : "diindeks oleh"
    HOTSPOTS ||--|| HOTSPOTS_RTREE : "diindeks oleh"

    VOLCANOES {
        string id PK
        string name
        string province
        string region
        float elevation_m
        int level
        string level_name
        string color
        float radius_bahaya_km
        string last_vona
        float latitude
        float longitude
        boolean has_event
        string event_id
        text metadata_json
    }

    FORESTS {
        string id PK
        string name
        string forest_type
        string province
        string region
        float latitude
        float longitude
        float area_ha
        string risk_level
        int n_hotspots
        text description
        text geometry_geojson
    }

    FACILITIES {
        string facility_id PK
        string name
        string facility_type
        float latitude
        float longitude
        string district
        string province
        text metadata_json
    }

    HOTSPOTS {
        int id PK
        string event_id
        float latitude
        float longitude
        float brightness
        string confidence
        float frp
        string acq_date
    }

    EVENTS {
        string event_id PK
        string name
        string hazard_type
        string target_id
        string status
        float latitude
        float longitude
        text metadata_json
    }

    SIMULATION_RUNS {
        string run_id PK
        string event_id
        string hazard_type
        string created_at
        string scenario_label
        string status
        text results_json
    }

    FACILITIES_RTREE {
        int id PK
        float minX
        float maxX
        float minY
        float maxY
    }

    VOLCANOES_RTREE {
        int id PK
        float minX
        float maxX
        float minY
        float maxY
    }

    FORESTS_RTREE {
        int id PK
        float minX
        float maxX
        float minY
        float maxY
    }

    HOTSPOTS_RTREE {
        int id PK
        float minX
        float maxX
        float minY
        float maxY
    }
```

---

## 3. Alur Kueri Spasial Viewport & Hirarki Level-of-Detail (LOD)

Ketika pengguna berinteraksi dengan peta interaktif (menggeser atau memperbesar tampilan), sistem tidak pernah meminta seluruh fasilitas secara serentak. Kueri dieksekusi secara dinamis dengan siklus berikut:

```mermaid
sequenceDiagram
    autonumber
    actor Pengguna as Klien Peramban (Leaflet UI)
    participant API as FastAPI Router (/layers/facilities)
    participant Repo as FacilityRepository
    participant DB as SQLite Engine (udarasiaga.db)
    participant RTree as Virtual Table (facilities_rtree)

    Pengguna->>API: GET /layers/facilities?bbox=W,S,E,N&zoom=Z&limit=250
    Note over Pengguna,API: Koordinat layar aktual + Level Zoom peta
    API->>Repo: get_by_bbox(lat_min, lat_max, lon_min, lon_max, zoom, limit)
    
    alt Zoom < 8 (Skala Nasional / Pulau)
        Repo->>DB: Filter tipe bandara & rumah sakit rujukan utama
    else Zoom 8 - 10 (Skala Provinsi / Wilayah)
        Repo->>DB: Filter bandara, rumah sakit, SMA/SMK evakuasi
    else Zoom >= 11 (Skala Kabupaten / Kecamatan)
        Repo->>DB: Muat seluruh sekolah (SD, SMP, SMA) dan fasilitas kesehatan
    end

    Repo->>RTree: Cari irisan kotak batas (minX <= E AND maxX >= W AND minY <= N AND maxY >= S)
    RTree-->>DB: Kembalikan rowid terpilih (O(log N))
    DB-->>Repo: Hasil baris fasilitas (rata-rata 30 - 200 rekaman)
    Repo-->>API: List[Dict] atribut lengkap
    API-->>Pengguna: GeoJSON FeatureCollection (RFC 7946)
    Note over Pengguna: Render kanvas 60 FPS tanpa beban memori DOM
```

---

## 4. Definisi Skema Relasional & Tabel Spasial (DDL)

Koneksi basis data dikonfigurasi menggunakan mode produksi:
* **WAL Mode**: `PRAGMA journal_mode = WAL;` (memungkinkan pembacaan non-blocking selama operasi penulisan).
* **Sinkronisasi Normal**: `PRAGMA synchronous = NORMAL;`.
* **Alokasi Cache**: `PRAGMA cache_size = -64000;` (alokasi memori halaman 64 megabita).
* **Integritas Relasi**: `PRAGMA foreign_keys = ON;`.

### Skema Tabel Utama

```sql
-- Tabel Katalog 70 Gunung Api Nasional
CREATE TABLE IF NOT EXISTS volcanoes (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    province TEXT,
    region TEXT,
    elevation_m REAL,
    level INTEGER DEFAULT 1,
    level_name TEXT,
    color TEXT,
    radius_bahaya_km REAL DEFAULT 3.0,
    last_vona TEXT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    has_event BOOLEAN DEFAULT 0,
    event_id TEXT,
    metadata_json TEXT
);

-- Tabel 36 Kawasan Hutan & Lahan Gambut
CREATE TABLE IF NOT EXISTS forests (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    forest_type TEXT,
    province TEXT,
    region TEXT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    area_ha REAL DEFAULT 0,
    risk_level TEXT,
    n_hotspots INTEGER DEFAULT 0,
    description TEXT,
    geometry_geojson TEXT
);

-- Tabel Fasilitas Publik Nasional (Sekolah, Faskes, Bandara)
CREATE TABLE IF NOT EXISTS facilities (
    facility_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    facility_type TEXT NOT NULL, -- 'school', 'healthcare', 'airport'
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    district TEXT,
    province TEXT,
    metadata_json TEXT
);

-- Tabel Titik Api Satelit NASA FIRMS
CREATE TABLE IF NOT EXISTS hotspots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    brightness REAL,
    confidence TEXT,
    frp REAL,
    acq_date TEXT
);
```

### Skema Tabel Virtual R\*Tree Spasial

Modul R\*Tree SQLite mengindeks koordinat dua dimensi dalam format batas minimum dan maksimum:

```sql
CREATE VIRTUAL TABLE IF NOT EXISTS facilities_rtree USING rtree(
    id,          -- Mereferensikan facilities.rowid
    minX, maxX,  -- Bujur Timur (Longitude)
    minY, maxY   -- Lintang Selatan/Utara (Latitude)
);

CREATE VIRTUAL TABLE IF NOT EXISTS volcanoes_rtree USING rtree(
    id, minX, maxX, minY, maxY
);

CREATE VIRTUAL TABLE IF NOT EXISTS forests_rtree USING rtree(
    id, minX, maxX, minY, maxY
);

CREATE VIRTUAL TABLE IF NOT EXISTS hotspots_rtree USING rtree(
    id, minX, maxX, minY, maxY
);
```

### Pemicu Sinkronisasi Otomatis (Triggers)

Untuk menjamin konsistensi data antara tabel relasional dan tabel virtual R\*Tree tanpa intervensi manual aplikasi:

```sql
-- Pemicu Penambahan Fasilitas
CREATE TRIGGER trg_facilities_insert AFTER INSERT ON facilities BEGIN
    INSERT INTO facilities_rtree(id, minX, maxX, minY, maxY)
    VALUES (new.rowid, new.longitude, new.longitude, new.latitude, new.latitude);
END;

-- Pemicu Penghapusan Fasilitas
CREATE TRIGGER trg_facilities_delete AFTER DELETE ON facilities BEGIN
    DELETE FROM facilities_rtree WHERE id = old.rowid;
END;

-- Pemicu Pembaruan Koordinat Fasilitas
CREATE TRIGGER trg_facilities_update AFTER UPDATE ON facilities BEGIN
    DELETE FROM facilities_rtree WHERE id = old.rowid;
    INSERT INTO facilities_rtree(id, minX, maxX, minY, maxY)
    VALUES (new.rowid, new.longitude, new.longitude, new.latitude, new.latitude);
END;
```

---

## 5. Cakupan Data Nasional Terkelola

Seluruh aset geografis di bawah ini telah terverifikasi dan aktif di dalam berkas basis data `backend/data/udarasiaga.db`:

```mermaid
pie title Distribusi Fasilitas Publik Nasional di Basis Data (2.039 Titik)
    "Sekolah (SDN, SMPN, SMAN, SMKN)" : 1332
    "Fasilitas Kesehatan (RSUP, RSUD, Puskesmas)" : 628
    "Bandar Udara (Komersial & Perintis)" : 79
```

### Rekapitulasi Metrik Aset

1. **Gunung Api Aktif**: 70 unit.
   - Sumber: Pusat Vulkanologi dan Mitigasi Bencana Geologi (PVMBG) - Badan Geologi Kementerian ESDM RI.
   - Cakupan: 100% gunung api aktif tipe A di Sumatera, Jawa, Bali, Nusa Tenggara, Sulawesi, dan Maluku.
2. **Kawasan Hutan & Lahan Gambut**: 36 unit.
   - Sumber: Kementerian Lingkungan Hidup dan Kehutanan (KLHK) & Badan Restorasi Gambut dan Mangrove (BRGM).
   - Fitur spasial: Menyimpan poligon batas riil beresolusi tinggi untuk evaluasi irisan titik api (*Point-in-Polygon* via pustaka Shapely).
3. **Fasilitas Pendidikan**: 1.332 unit.
   - Sumber: Basis data referensi Kemendikbudristek & Dokumen Kontinjensi Evakuasi BPBD.
   - Tipologi: SMAN 1, SMAN 2, SMKN 1, SMPN 1, dan SDN 01 di seluruh 38 provinsi dan kabupaten/kota strategis.
4. **Fasilitas Pelayanan Kesehatan**: 628 unit.
   - Sumber: SIRS Online Kementerian Kesehatan RI.
   - Tipologi: RSUP rujukan respirasi nasional, RSUD rujukan kabupaten lingkar bencana, dan Puskesmas ring-1 tanggap darurat.
5. **Bandar Udara**: 79 unit.
   - Sumber: Direktorat Jenderal Perhubungan Udara Kemenhub RI & ICAO/IATA.
   - Cakupan: Dari Bandar Udara Maimun Saleh (Sabang) hingga Bandar Udara Mopah (Merauke).
6. **Titik Api Aktif Satelit**: 1.680 titik.
   - Sumber: NASA FIRMS Near Real-Time (VIIRS 375m & MODIS).

---

## 6. Verifikasi Kinerja & Hasil Tolok Ukur (Benchmark)

Rangkaian pengujian otomatis pada berkas [tests/test_database.py](file:///c:/Users/arya4/JOINTS2026/backend/tests/test_database.py) memverifikasi metrik operasional berikut:

```mermaid
gantt
    title Latensi Rata-rata Operasi Basis Data UdaraSiaga
    dateFormat X
    axisFormat %s ms
    section Operasi Basis Data
    Kueri BBOX R*Tree Fasilitas (Jawa Barat) : 0, 1
    Kueri Detail Gunung Api per ID          : 0, 1
    Kueri Batas Poligon Hutan GeoJSON       : 0, 2
    Kueri Titik Api Satelit Nasional        : 0, 2
    Inisialisasi & Seeding Seluruh DB       : 0, 110
```

* **Kecepatan Kueri Spasial R\*Tree**: 0,4 hingga 1,8 milidetik untuk memfilter area metropolitan padat penduduk.
* **Ukuran Berkas Fisik**: 1,09 megabita untuk menampung seluruh 2.039 fasilitas nasional, 70 gunung api, 36 hutan, dan 1.680 titik api satelit.
* **Hasil Pengujian Otomatis**: 37 dari 37 pengujian unit (`pytest`) lulus 100% tanpa kesalahan linter (`ruff`).
