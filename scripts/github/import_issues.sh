#!/usr/bin/env bash
# Usage:
#   gh auth login
#   gh auth refresh -s project      # needed to add issues to a Project
#   REPO="nyarikerja/<repo-name>" PROJECT_OWNER="nyarikerja" PROJECT_NUMBER=1 bash import_issues.sh
set -e
: "${REPO:?set REPO=owner/name}"
: "${PROJECT_OWNER:?set PROJECT_OWNER=org or user that owns the project}"
: "${PROJECT_NUMBER:?set PROJECT_NUMBER=project number}"

S1="Sprint 1 - Fondasi & Desain"
S2="Sprint 2 - Pengembangan Inti"
S3="Sprint 3 - Integrasi & QA"
S4="Sprint 4 - Buffer & Submit"

echo "== Labels"
for l in area:be-gunung area:be-karhutla area:fe area:uiux area:deck area:video area:proposal area:qa area:setup P0 P1 P2 bug; do
  gh label create "$l" --repo "$REPO" --force >/dev/null
done

echo "== Milestones"
mk_ms() { gh api "repos/$REPO/milestones" -f title="$1" -f due_on="$2T23:59:00Z" >/dev/null 2>&1 || true; }
mk_ms "$S1" 2026-10-09
mk_ms "$S2" 2026-10-12
mk_ms "$S3" 2026-10-14
mk_ms "$S4" 2026-10-16

echo "== Issues"
# mk "title" "milestone" "labels" "PIC / due"
mk() {
  url=$(gh issue create --repo "$REPO" \
    --title "$1" --milestone "$2" --label "$3" --body "PIC: $4")
  gh project item-add "$PROJECT_NUMBER" --owner "$PROJECT_OWNER" --url "$url" >/dev/null
  echo "  + $1"
}

# ---------- Sprint 1 ----------
mk "Registrasi tim ke JOINTS UGM" "$S1" "area:setup,P0" "Semua (Arya submit) | 8 Okt"
mk "Finalisasi judul, GSM, dan tema" "$S1" "area:setup,P0" "Semua | 7 Okt"
mk "Setup repo, branch protection, PR template, .env.example" "$S1" "area:setup,P0" "Arya | 7 Okt"
mk "Tulis kontrak API (/simulate, /events, /schools, /hospitals) di docs/api-contract.md" "$S1" "area:setup,P0" "Arya + Bokem | 7 Okt"
mk "Buat sample response JSON statis (gunung & karhutla) sebagai mock FE" "$S1" "area:setup,P0" "Arya + Bokem | 8 Okt"
mk "Wireframe layout (peta, laci kanan 5 tab, legenda, timeline)" "$S1" "area:uiux,P0" "Zaki/Adit | 7 Okt"
mk "High-fidelity UI (palet hazard-aware, 3 kontur, kartu sekolah, badge Skenario Hipotetis)" "$S1" "area:uiux,P0" "Zaki/Adit | 9 Okt"
mk "Scaffold FE (Leaflet dark map, laci, mode Otomatis/Coba-coba) dengan mock JSON" "$S1" "area:fe,P0" "Zaki/Adit | 9 Okt"
mk "Pitch deck: outline, narasi masalah, pembagian slide" "$S1" "area:deck,P0" "Semua | 7 Okt"
mk "Riset akses API (FIRMS key, Open-Meteo, Overpass, WorldPop) + fixture offline" "$S1" "area:be-karhutla,P0" "Bokem | 9 Okt"

# ---------- Sprint 2: BE Gunung ----------
mk "Loader katalog 20 gunung api + data VONA (cache data/events/)" "$S2" "area:be-gunung,P0" "Arya | 12 Okt"
mk "Fetch angin multi-aras Open-Meteo + fixture offline" "$S2" "area:be-gunung,P0" "Arya | 12 Okt"
mk "Konversi MER Mastin (2009) dari tinggi kolom" "$S2" "area:be-gunung,P0" "Arya | 10 Okt"
mk "Mesin partikel Lagrangian RK2 + difusi turbulen (modul bersama)" "$S2" "area:be-gunung,P0" "Arya | 10 Okt"
mk "Ensemble paralel 15-51 anggota + probabilitas raster" "$S2" "area:be-gunung,P0" "Arya | 11 Okt"
mk "Gaussian smoothing + MultiPolygon kontur P90/P50/P05" "$S2" "area:be-gunung,P0" "Arya | 11 Okt"
mk "Wet scavenging + peringatan lahar dingin" "$S2" "area:be-gunung,P1" "Arya | 12 Okt"
mk "Eksposur populasi WorldPop, rentang P5-P50-P95 (anak & lansia)" "$S2" "area:be-gunung,P0" "Arya | 12 Okt"
mk "Triase sekolah (>=40%, 15-39%, <15%) + ETA tercepat dari data OSM" "$S2" "area:be-gunung,P0" "Arya | 12 Okt"
mk "RS Aman Bebas Abu + rute evakuasi" "$S2" "area:be-gunung,P1" "Arya | 12 Okt"
mk "Estimasi hektare pertanian & sumber air" "$S2" "area:be-gunung,P2" "Arya | 12 Okt"

# ---------- Sprint 2: BE Karhutla ----------
mk "Fetch NASA FIRMS (VIIRS) + cache hotspot Kalimantan" "$S2" "area:be-karhutla,P0" "Bokem | 10 Okt"
mk "Konversi FRP ke emisi PM2.5 (Wooster 2005) + pengali gambut 2,34x" "$S2" "area:be-karhutla,P0" "Bokem | 11 Okt"
mk "Integrasi ke mesin RK2 milik Arya (tanpa engine kedua)" "$S2" "area:be-karhutla,P0" "Bokem | 12 Okt"
mk "Endpoint /simulate karhutla sesuai kontrak API" "$S2" "area:be-karhutla,P0" "Bokem | 12 Okt"
mk "Klaster & ranking hotspot (prioritas water bombing)" "$S2" "area:be-karhutla,P1" "Bokem | 12 Okt"
mk "Simulasi intervensi pemadaman 5 klaster teratas" "$S2" "area:be-karhutla,P1" "Bokem | 12 Okt"
mk "Hitungan CO2e" "$S2" "area:be-karhutla,P1" "Bokem | 12 Okt"

# ---------- Sprint 2: FE ----------
mk "Render 3 kontur probabilitas + legenda dinamis" "$S2" "area:fe,P0" "Zaki/Adit | 11 Okt"
mk "Timeline player T+0 s.d. T+48 (play/pause, lompat 6 jam)" "$S2" "area:fe,P0" "Zaki/Adit | 11 Okt"
mk "Laci kanan: Tab Dampak, Sekolah, Rujukan Medis" "$S2" "area:fe,P0" "Zaki/Adit | 12 Okt"
mk "Mode Coba-coba (slider tinggi kolom, FRP, hujan) + watermark Skenario Hipotetis" "$S2" "area:fe,P0" "Zaki/Adit | 12 Okt"
mk "Tab Edukasi APD (N95, larangan softlens)" "$S2" "area:fe,P1" "Zaki/Adit | 12 Okt"
mk "Tab Validasi: katalog asumsi D01-D24 (JSON statis) + grafik sensitivitas" "$S2" "area:fe,P1" "Zaki/Adit | 12 Okt"
mk "Ekspor ringkasan satu halaman + tombol Putar Demo" "$S2" "area:fe,P2" "Zaki/Adit | 12 Okt"

# ---------- Sprint 2: Deck & Proposal ----------
mk "Pitch deck draft 1" "$S2" "area:deck,P0" "Semua | 11 Okt"
mk "Proposal: mulai penulisan" "$S2" "area:proposal,P0" "Claude + tim | 12 Okt"

# ---------- Sprint 3 ----------
mk "Integrasi BE ke FE (gunung dulu, lalu karhutla)" "$S3" "area:fe,area:be-gunung,P0" "Arya (Zaki/Adit support) | 13 Okt"
mk "Fallback offline: demo jalan tanpa internet" "$S3" "area:be-gunung,P0" "Arya | 13 Okt"
mk "QA skenario gunung (min. 3 gunung berbeda)" "$S3" "area:qa,P0" "Semua | 14 Okt"
mk "QA skenario karhutla Kalimantan" "$S3" "area:qa,P0" "Semua | 14 Okt"
mk "Cek responsive & performa waktu simulasi" "$S3" "area:qa,P1" "Zaki/Adit | 14 Okt"
mk "Bug bash (bug jadi issue berlabel bug)" "$S3" "area:qa,P0" "Semua | 14 Okt"
mk "Feature freeze jam 20.00" "$S3" "area:setup,P0" "Semua | 14 Okt"
mk "Rekam demo & edit video" "$S3" "area:video,P0" "Bokem | start 14 Okt"
mk "Pitch deck final + latihan" "$S3" "area:deck,P0" "Semua | 14 Okt"
mk "Proposal final" "$S3" "area:proposal,P0" "Semua + Claude | 14 Okt"

# ---------- Sprint 4 ----------
mk "Fix bug kritis pasca-freeze" "$S4" "bug,P0" "Semua | 15 Okt"
mk "Finalisasi video" "$S4" "area:video,P0" "Bokem | 15 Okt"
mk "Cek kelengkapan file submission" "$S4" "area:setup,P0" "Semua | 15 Okt"
mk "Submit ke portal (cadangan tanggal 16)" "$S4" "area:setup,P0" "Arya | 15 Okt"

echo "Done."
