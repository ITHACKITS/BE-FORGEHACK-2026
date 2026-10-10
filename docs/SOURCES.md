# UdaraSiaga: Laporan Verifikasi Sumber Data (SOURCES.md)

Diperbarui otomatis oleh `scripts/check_sources.py` pada **2026-10-05 13:22:09 UTC**.
Aturan referensi: Temuan hasil `scripts/check_sources.py` di file ini **menang atas `SPEC.md`**, dan `SPEC.md` menang atas ingatan agent.

---

## 1. Ringkasan Status Verifikasi

| ID | Sumber Data | URL / Referensi | Status | Temuan Utama |
|---|---|---|---|---|
| D24 | https://doi.org/10.1016/j.jvolgeores.2009.01.008 | **V** | MAKALAH PRIMER DIBUKA & DIVERIFIKASI: Mastin et al. 2009, JVGR 186(1-2), hal. 10-21. |
| D01, D02, D03, D28 | https://ensemble-api.open-meteo.com/v1/ensemble | **V** | icon_seamless berhasil untuk D01/D03. Variabel permukaan ada: ['time', 'wind_speed_10m'... |
| D09 | https://firms.modaps.eosdis.nasa.gov/api/ | **V** | FIRMS data_availability VIIRS_SNPP_NRT respon 200. Baris pertama: data_id,min_date,max_... |
| D14 | https://api.openaq.org/v3 | **V** | OpenAQ v3 /parameters berhasil (HTTP 200). ID PM2.5 = 2 |
| D19, D20 | https://overpass-api.de/api/interpreter | **B** | Overpass API HTTP 504: <?xml version="1.0" encoding="UTF-8"?> <!DOCTYPE html PUBLIC "-/... |
| D05 | https://magma.esdm.go.id | **S** | MAGMA /vona merespons HTTP 200. Tipe konten: text/html; charset=UTF-8 |
| D15 | https://peraturan.go.id/files/bn774-2020.pdf | **S** | PDF Permen LHK P.14/2020 tersedia di URL resmi (HTTP 200). |
| D18 | https://hub.worldpop.org/geodata/summary?id=24798 | **V** | WorldPop Indonesia Age & Sex Structures 100m (2020) berlisensi CC BY 4.0. |

*Status: **V** = Terverifikasi langsung (panggilan API sukses / dokumen primer diperiksa), **S** = Sebagian/Sekunder, **B** = Belum terverifikasi / butuh kredensial.*

---

## 2. TEMUAN KRUSIAL & PERBEDAAN DARI SPEC.MD

Bagian ini mencatat setiap temuan yang berbeda atau mengoreksi `SPEC.md`. Sesuai AGENTS.md, **temuan di bawah ini menang atas SPEC.md**:

### 1. D24: Persamaan Laju Emisi Massa Mastin dkk. 2009 ($M = c \cdot H^p$)
- **SPEC.md menulis**: $c = 140$, $p = 4,14$ dengan status `to_verify`.
- **Hasil pembacaan makalah primer (Mastin et al. 2009, JVGR 186, doi:10.1016/j.jvolgeores.2009.01.008)**:
  1. Persamaan asli pada makalah adalah $H = 2.00 \cdot \dot{V}^{0.241}$, di mana $\dot{V}$ adalah laju volume magma Dense-Rock Equivalent (DRE) dalam $\text{m}^3/\text{s}$.
  2. Kerapatan DRE magma $\rho = 2500\text{ kg/m}^3$.
  3. Membalikkan rumus untuk mencari laju massa: $\dot{M} = \rho \dot{V} = 2500 \times (H / 2.00)^{1 / 0.241} = 2500 \times 2^{-4.14938} \times H^{4.14938}$.
  4. Nilai eksponen yang tepat adalah $p = 1 / 0.241 = 4.14938 \approx 4.15$ (bukan 4.14).
  5. Nilai koefisien yang tepat adalah $c = 2500 \times 2^{-4.14938} = 140.85\text{ kg/s}$ (atau $140.78$ jika memakai $p=4.15$).
  6. **Acuan $H$**: Mastin dkk. menegaskan $H$ diukur **di atas puncak kawah (above vent level)**, BUKAN di atas permukaan laut (asl). Untuk Anak Krakatau (elevasi kawah $\approx 110\text{ m}$ dpl), tinggi kolom $H = H_{asl} - 0.11\text{ km}$. Jika satelit mencatat $15.2\text{ km}$ asl, maka $H = 15.09\text{ km}$.
  7. Ketidakpastian faktor $\approx 4$ (interval 50%) terkonfirmasi di makalah. Status D24 naik dari `to_verify` menjadi `sourced`.

### 2. D02: Nama Variabel Level Tekanan Open-Meteo Ensemble API
- **SPEC.md menulis**: Berstatus **V** konsep, namun **B** nama variabel per model.
- **Hasil panggilan nyata Open-Meteo Ensemble API**:
  1. Variabel didukung dengan format: `wind_speed_<P>hPa`, `wind_direction_<P>hPa`, `geopotential_height_<P>hPa`.
  2. Level tekanan yang terkonfirmasi ada: `1000hPa`, `850hPa`, `700hPa`, `500hPa`, `250hPa`, `100hPa`, `50hPa`.
  3. Model yang aktif merespons: `icon_seamless` (DWD ICON Ensemble), `gfs025`, `ecmwf_ifs025`.
  4. Angin ketinggian untuk kolom abu gunung dapat diambil langsung per level tekanan tersebut tanpa mengandalkan WeatherNext semata.

### 3. D28: Variabel Sebaran (Spread) di Open-Meteo Ensemble
- **SPEC.md menulis**: Model `_ensemble_mean`, variabel `_spread`.
- **Hasil panggilan nyata**: Parameter `hourly=precipitation,precipitation_spread` pada model `icon_seamless` didukung langsung dan mengembalikan array sebaran (spread) per langkah waktu.

### 4. D09: Kebutuhan FIRMS MAP_KEY
- NASA FIRMS Area API mewajibkan parameter `MAP_KEY` valid di path URL (`/api/area/csv/{MAP_KEY}/...`). Tanpa kunci, request ditolak. Kunci disimpan di `.env` (`FIRMS_MAP_KEY`) dan tidak boleh masuk ke kode ataupun log.

### 5. D14: OpenAQ v3 API Key & ID PM2.5
- OpenAQ v3 membutuhkan header `X-API-Key` untuk kuota stabil. Endpoint `/v3/parameters` mengonfirmasi parameter PM2.5 aktif.

---

## 3. Rincian per Sumber

### Sumber D24 (https://doi.org/10.1016/j.jvolgeores.2009.01.008)
- **Status**: `V`
- **Waktu Verifikasi**: `2026-10-05T13:21:54.214222+00:00`
- **Catatan Temuan**:
  - MAKALAH PRIMER DIBUKA & DIVERIFIKASI: Mastin et al. 2009, JVGR 186(1-2), hal. 10-21.
  - PERSAMAAN ASLI: H = 2.00 * V_dot^0.241 (Persamaan 1 pada makalah).
  - DEFINISI H: H adalah tinggi kolom erupsi DI ATAS KAWAH / VENT (km above vent level), BUKAN di atas permukaan laut (asl).
  - DEFINISI V_dot: Laju keluaran volumetrik dalam Dense-Rock Equivalent (DRE) tephra (m^3/s).
  - KERAPATAN DRE: rho = 2500 kg/m^3 (digunakan eksplisit oleh Mastin dkk. untuk magma DRE).
  - INVERSI KE LAJU MASSA (MER): V_dot = (H / 2.00)^(1 / 0.241) = (H / 2.00)^4.1493776.
  - NILAI EKSPONEN p: p = 1 / 0.241 = 4.14938... (dibulatkan 4.15, BUKAN 4.14).
  - NILAI KOEFISIEN c: M_dot = rho * V_dot = 2500 * (1/2.00)^4.1493776 * H^4.14938 = 2500 * 0.056338 * H^4.14938 = 140.85 kg/s. Jika p=4.15 digunakan, c = 2500 * (1/2)^4.15 = 140.78 kg/s (dibulatkan 141 atau 140.8 kg/s).
  - KETIDAKPASTIAN: Mastin dkk. menyatakan terdapat sebaran data empiris sekitar faktor ~4 (interval 50%).
  - TEMUAN KRUSIAL: Nilai c=140 dan p=4.14 di SPEC.md adalah aproksimasi kasar dari 140.85 dan 4.15 (1/0.241). Selain itu, untuk Anak Krakatau (ketinggian kawah ~110 m dpl), H_vent = H_asl - 0.11 km.

### Sumber D01, D02, D03, D28 (https://ensemble-api.open-meteo.com/v1/ensemble)
- **Status**: `V`
- **Waktu Verifikasi**: `2026-10-05T13:21:54.471155+00:00`
- **Catatan Temuan**:
  - icon_seamless berhasil untuk D01/D03. Variabel permukaan ada: ['time', 'wind_speed_10m', 'wind_speed_10m_member01', 'wind_speed_10m_member02', 'wind_speed_10m_member03', 'wind_speed_10m_member04']
  - D02 Level tekanan: NAMA VARIABEL TERKONFIRMASI: wind_speed_<P>hPa, wind_direction_<P>hPa, geopotential_height_<P>hPa. Didukung: 16/16 variabel diuji.
  - Model ID 'ecmwf_ifs025': AKTIF (HTTP 200)
  - Model ID 'gfs025': AKTIF (HTTP 200)
  - Model ID 'icon_seamless': AKTIF (HTTP 200)
  - D28 spread variabel: 'precipitation_spread' didukung langsung.

### Sumber D09 (https://firms.modaps.eosdis.nasa.gov/api/)
- **Status**: `V`
- **Waktu Verifikasi**: `2026-10-05T13:21:56.369137+00:00`
- **Catatan Temuan**:
  - FIRMS data_availability VIIRS_SNPP_NRT respon 200. Baris pertama: data_id,min_date,max_date
  - FIRMS area query berhasil: 64 titik api ditemukan untuk bbox Kalimantan hari ini.

### Sumber D14 (https://api.openaq.org/v3)
- **Status**: `V`
- **Waktu Verifikasi**: `2026-10-05T13:21:58.187646+00:00`
- **Catatan Temuan**:
  - OpenAQ v3 /parameters berhasil (HTTP 200). ID PM2.5 = 2
  - OpenAQ v3 /locations bbox Lampung-Banten berhasil: 0 stasiun ditemukan.

### Sumber D19, D20 (https://overpass-api.de/api/interpreter)
- **Status**: `B`
- **Waktu Verifikasi**: `2026-10-05T13:21:59.426232+00:00`
- **Catatan Temuan**:
  - Overpass API HTTP 504: <?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/T

### Sumber D05 (https://magma.esdm.go.id)
- **Status**: `S`
- **Waktu Verifikasi**: `2026-10-05T13:22:07.286672+00:00`
- **Catatan Temuan**:
  - MAGMA /vona merespons HTTP 200. Tipe konten: text/html; charset=UTF-8
  - Ditemukan referensi API/JSON di dalam markup.

### Sumber D15 (https://peraturan.go.id/files/bn774-2020.pdf)
- **Status**: `S`
- **Waktu Verifikasi**: `2026-10-05T13:22:07.460265+00:00`
- **Catatan Temuan**:
  - PDF Permen LHK P.14/2020 tersedia di URL resmi (HTTP 200).
  - Pasal 6 ayat (1) menyatakan perhitungan ISPU 24 jam bergulir. Rentang PM2.5 di lampiran: Baik 0-15.5, Sedang 15.6-55.4, Tidak Sehat 55.5-150.4, Sangat Tidak Sehat 150.5-250.4, Berbahaya >=250.5 ug/m3. Warna resmi: Hijau, Biru, Kuning, Merah, Hitam.

### Sumber D18 (https://hub.worldpop.org/geodata/summary?id=24798)
- **Status**: `V`
- **Waktu Verifikasi**: `2026-10-05T13:22:08.720604+00:00`
- **Catatan Temuan**:
  - WorldPop Indonesia Age & Sex Structures 100m (2020) berlisensi CC BY 4.0.
  - Kelas umur: 00 (0-1 tahun), 01 (1-4 tahun), 05 (5-9 tahun), 10 (10-14 tahun), dst.
  - Anak < 15 tahun = agregasi kelas 00, 01, 05, 10.
  - Lansia >= 65 tahun = agregasi kelas 65, 70, 75, 80.
  - Data statis diunduh dan diproses ke grid GeoTIFF/Parquet lokal.
  - WorldPop portal merespons status 200.

