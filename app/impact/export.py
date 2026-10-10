"""
app/impact/export.py

Generator Dokumen Ringkasan Eksekutif & Lembar Aksi Darurat (Printable HTML & JSON).
Dirancang khusus untuk pimpinan BPBD, Dinas Kesehatan, Satuan Pendidikan, dan Relawan Lapangan.
Bebas dari tabel parameter matematika mentah internal, berfokus penuh pada instruksi taktis lapangan,
edukasi APD medis, perlindungan kelompok rentan, dan jaringan evakuasi fasilitas kesehatan.
"""

from typing import Any, Dict


def generate_printable_html(export_data: Dict[str, Any]) -> str:
    """
    Menghasilkan dokumen taktis HTML cetak mandiri (A4 print-ready)
    berstandar profesional kementerian/lembaga kebencanaan.
    """
    run_id = export_data.get("run_id", "-")
    hazard = export_data.get("hazard", "-").upper()
    mode = export_data.get("mode", "auto")
    scenario_label = export_data.get("scenario_label", "-")
    disclaimer = export_data.get("disclaimer", "")
    n_members = export_data.get("n_members", "-")
    horizon = export_data.get("horizon_hours", "-")
    members_source = export_data.get("members_source", "-")

    impact = export_data.get("impact", {})
    pop = impact.get("population_exposed", {"min": 0, "median": 0, "max": 0})
    child = impact.get("children_exposed", {"min": 0, "median": 0, "max": 0})
    elder = impact.get("elderly_exposed", {"min": 0, "median": 0, "max": 0})
    area = impact.get("area_exposed_km2", {"min": 0, "median": 0, "max": 0})
    schools_metric = impact.get("schools_exposed", {"min": 0, "median": 0, "max": 0})
    hc_metric = impact.get("healthcare_exposed", {"min": 0, "median": 0, "max": 0})

    def fmt_r(m: dict) -> str:
        return f"{m.get('min', 0):,.0f} &ndash; <strong>{m.get('median', 0):,.0f}</strong> &ndash; {m.get('max', 0):,.0f}"

    advisory = export_data.get("advisory", {})
    alert_level = advisory.get("alert_level", "SIAGA TANGGAP DARURAT")
    badge_bg = advisory.get("badge_bg", "#dc2626")

    # Ambil daftar RS rujukan aman terdekat jika tersedia
    facilities = export_data.get("facilities", {})
    safe_hospitals = facilities.get("evacuation_referral_hospitals", [])[:4]
    schools_at_risk = facilities.get("schools", [])[:5]

    hospitals_rows = ""
    if safe_hospitals:
        for h in safe_hospitals:
            hospitals_rows += f"""
            <tr>
              <td><strong>{h.get('name')}</strong><br><small style='color:#64748b;'>{h.get('district', '-')}</small></td>
              <td><span style='color:#059669;font-weight:700;'>{h.get('status_badge', 'ZONA AMAN')}</span></td>
              <td><strong>{h.get('distance_from_epicenter_km', '-')} km</strong></td>
              <td><small>{h.get('emergency_hotline', 'SPGDT 119')}</small></td>
            </tr>
            """
    else:
        hospitals_rows = """
        <tr>
          <td colspan='4' style='text-align:center;color:#64748b;'>Data spesifik fasilitas kesehatan rujukan dimuat dari peta taktis. Hubungi SPGDT 119 untuk koordinasi ambulans.</td>
        </tr>
        """

    schools_rows = ""
    if schools_at_risk:
        for s in schools_at_risk:
            prob_pct = s.get('exposure_pct', int(round(s.get('exposure_probability', 0) * 100)))
            schools_rows += f"""
            <tr>
              <td><strong>{s.get('name')}</strong><br><small style='color:#64748b;'>{s.get('district', '-')}</small></td>
              <td><strong style='color:#dc2626;'>{prob_pct}%</strong></td>
              <td><span style='background:#fee2e2;color:#991b1b;padding:2px 6px;border-radius:3px;font-size:8pt;font-weight:600;'>{s.get('recommendation', 'ALIHKAN KE PJJ')}</span></td>
              <td><small>{s.get('action_detail', '-')}</small></td>
            </tr>
            """
    else:
        schools_rows = """
        <tr>
          <td colspan='4' style='text-align:center;color:#64748b;'>Seluruh sekolah berada di luar batas ambang paparan langsung (&lt; 5% risiko). KBM tatap muka dapat berlangsung normal.</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <title>Standbai preparedness summary - {run_id}</title>
  <style>
    @page {{ size: A4; margin: 12mm 14mm; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 10pt;
      line-height: 1.35;
      color: #0f172a;
      margin: 0;
      padding: 0;
    }}
    .header {{
      border-bottom: 2px solid #0f172a;
      padding-bottom: 6px;
      margin-bottom: 10px;
      display: flex;
      justify-content: space-between;
      align-items: baseline;
    }}
    .brand {{ font-size: 16pt; font-weight: 800; letter-spacing: -0.5px; color: #0f172a; }}
    .subtitle {{ font-size: 9.5pt; color: #475569; font-weight: 600; }}
    .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    .alert-banner {{
      background: {badge_bg};
      color: #ffffff;
      padding: 6px 10px;
      font-size: 10pt;
      font-weight: 700;
      border-radius: 4px;
      margin-bottom: 10px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .disclaimer-box {{
      background: #fff1f2;
      border-left: 3px solid #e11d48;
      padding: 6px 10px;
      font-size: 8pt;
      color: #881337;
      margin-bottom: 10px;
      line-height: 1.3;
    }}
    .meta-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 6px;
      margin-bottom: 12px;
      background: #f8fafc;
      padding: 6px 10px;
      border: 1px solid #e2e8f0;
      font-size: 8.5pt;
    }}
    .meta-item strong {{ display: block; font-size: 7.5pt; text-transform: uppercase; color: #64748b; }}
    h2 {{
      font-size: 10.5pt;
      border-bottom: 1.5px solid #cbd5e1;
      padding-bottom: 3px;
      margin-top: 10px;
      margin-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: 0.3px;
      color: #0f172a;
    }}
    table {{ width: 100%; border-collapse: collapse; margin-bottom: 10px; font-size: 8.5pt; }}
    th, td {{ border: 1px solid #cbd5e1; padding: 4px 6px; text-align: left; }}
    th {{ background: #f1f5f9; font-weight: 600; color: #334155; }}
    .protocol-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin-bottom: 10px;
    }}
    .protocol-card {{
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 4px;
      padding: 6px 8px;
      font-size: 8.5pt;
    }}
    .protocol-card h3 {{
      margin: 0 0 4px 0;
      font-size: 9pt;
      color: #0f172a;
      border-bottom: 1px dashed #e2e8f0;
      padding-bottom: 2px;
    }}
    .warning-text {{ color: #b91c1c; font-weight: 700; }}
    .success-text {{ color: #047857; font-weight: 700; }}
    .footer {{
      margin-top: 14px;
      border-top: 1px solid #cbd5e1;
      padding-top: 6px;
      font-size: 7.5pt;
      color: #64748b;
      display: flex;
      justify-content: space-between;
    }}
    @media print {{
      body {{ font-size: 9pt; }}
      .no-print {{ display: none; }}
    }}
  </style>
</head>
<body>
  <div class="header">
    <div>
      <span class="brand">Standbai</span>
      <span class="subtitle"> | Action sheet &amp; preparedness summary</span>
    </div>
    <div class="mono" style="font-size:8pt;color:#64748b;">ID Skenario: {run_id}</div>
  </div>

  <div class="alert-banner">
    <span>TINGKAT PERINGATAN: {alert_level}</span>
    <span style="font-size:8.5pt;font-weight:400;">Horizon Simulasi: T + {horizon} Jam</span>
  </div>

  <div class="disclaimer-box">
    <strong>DISCLAIMER OTORITATIF:</strong> {disclaimer}
  </div>

  <div class="meta-grid">
    <div class="meta-item"><strong>Jenis Bahaya:</strong> {hazard}</div>
    <div class="meta-item"><strong>Skenario / Lokasi:</strong> {scenario_label}</div>
    <div class="meta-item"><strong>Ansambel Fisika:</strong> {n_members} anggota ({members_source})</div>
    <div class="meta-item"><strong>Integritas Data:</strong> Multi-Satelit &amp; Telemetri PVMBG/BMKG</div>
  </div>

  <h2>1. Estimasi Dampak Populasi &amp; Paparan Spasial (P5 &ndash; P50 &ndash; P95)</h2>
  <table>
    <thead>
      <tr>
        <th>Indikator Dampak</th>
        <th>Rentang Ketidakpastian Ansambel {{Min &ndash; Median &ndash; Maks}}</th>
        <th>Satuan</th>
        <th>Metodologi &amp; Keterangan</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Penduduk Terpapar (Total)</strong></td>
        <td class="mono">{fmt_r(pop)}</td>
        <td>Jiwa</td>
        <td>Tumpang tindih grid populasi resolusi tinggi dengan jejak sebaran</td>
      </tr>
      <tr>
        <td>Anak-anak (&lt;15 Tahun)</td>
        <td class="mono">{fmt_r(child)}</td>
        <td>Jiwa</td>
        <td>Kelompok paling rentan iritasi saluran pernapasan atas &amp; asma</td>
      </tr>
      <tr>
        <td>Lansia (&ge;65 Tahun)</td>
        <td class="mono">{fmt_r(elder)}</td>
        <td>Jiwa</td>
        <td>Kelompok risiko tinggi komplikasi kardiopulmoner &amp; PPOK</td>
      </tr>
      <tr>
        <td>Luas Jejak Sebaran (Footprint)</td>
        <td class="mono">{fmt_r(area)}</td>
        <td>km&sup2;</td>
        <td>Luas area kumulatif yang terlewati konsentrasi berbahaya</td>
      </tr>
      <tr>
        <td>Fasilitas Publik Berisiko</td>
        <td class="mono">Sekolah: {fmt_r(schools_metric)} | Faskes: {fmt_r(hc_metric)}</td>
        <td>Unit</td>
        <td>Fasilitas di dalam jangkauan trajektori abu/asap</td>
      </tr>
    </tbody>
  </table>

  <h2>2. Panduan Standar Alat Pelindung Diri (APD) Kemenkes RI &amp; PERDAMI</h2>
  <div class="protocol-grid">
    <div class="protocol-card">
      <h3>Perlindungan Saluran Pernapasan (Masker)</h3>
      <div><span class="success-text">&bull; WAJIB: Respirator Partikulat N95 / KN95 / KF94</span></div>
      <div style="font-size:8pt;margin-bottom:4px;">Menyaring &ge; 95% partikel silika sub-mikron &amp; PM2.5. Klip hidung wajib ditekan rapat kedap udara.</div>
      <div><span class="warning-text">&bull; DILARANG: Masker Bedah 3-Ply &amp; Masker Kain</span></div>
      <div style="font-size:8pt;">Pori-pori terlalu longgar dan kebocoran samping 30%&ndash;50%. Partikel abu silika tetap leluasa masuk paru-paru.</div>
    </div>
    <div class="protocol-card">
      <h3>Perlindungan Mata &amp; Anggota Tubuh</h3>
      <div><span class="warning-text">&bull; DILARANG KERAS MEMAKAI LENSA KONTAK (SOFTLENS)!</span></div>
      <div style="font-size:8pt;margin-bottom:4px;">Kristal kaca silika abu vulkanik tajam akan menggores kornea di bawah lensa, berisiko <strong>abrasi kornea &amp; kebutaan permanen</strong>.</div>
      <div><span class="success-text">&bull; WAJIB: Kacamata Pelindung Tertutup (Safety Goggles)</span></div>
      <div style="font-size:8pt;">Gunakan kacamata pelindung tertutup lis karet serta pakaian lengan panjang untuk mencegah dermatitis asam.</div>
    </div>
  </div>

  <h2>3. Protokol Satuan Pendidikan (Sekolah Aman Bencana - SPAB)</h2>
  <table>
    <thead>
      <tr>
        <th>Nama Sekolah</th>
        <th>Peluang Paparan</th>
        <th>Instruksi Operasional</th>
        <th>Tindakan Dini yang Wajib Dilakukan</th>
      </tr>
    </thead>
    <tbody>
      {schools_rows}
    </tbody>
  </table>

  <h2>4. Koridor Evakuasi Medis &amp; Rumah Sakit Rujukan Aman Terdekat</h2>
  <table>
    <thead>
      <tr>
        <th>Rumah Sakit Rujukan Aman</th>
        <th>Status Zona Udara</th>
        <th>Jarak dari Episentrum</th>
        <th>Kontak Darurat / Call Center</th>
      </tr>
    </thead>
    <tbody>
      {hospitals_rows}
    </tbody>
  </table>

  <div class="protocol-grid" style="margin-top:6px;">
    <div class="protocol-card">
      <h3>Perlindungan Sumber Air Bersih Pemukiman</h3>
      <div style="font-size:8pt;">
        Segera tutup seluruh tandon air minum, sumur gali, dan penampungan dengan terpal atau plastik kedap. Abu vulkanik mengandung fluorida, sulfat, dan logam berat yang mencemari air minum.
      </div>
    </div>
    <div class="protocol-card">
      <h3>Pembersihan Abu Rumah Tangga (Dilarang Menyapu Kering)</h3>
      <div style="font-size:8pt;">
        Dilarang menyapu abu kering karena menerbangkan partikel kembali ke udara. Semprotkan air halus lalu pel secara basah. Bersihkan atap rumah sebelum hujan turun agar tidak rubuh karena beban abu basah.
      </div>
    </div>
  </div>

  <div class="footer">
    <div>Generated by Standbai, a tool for learning and preparing. Not an official warning. Follow BMKG, PVMBG and your local BPBD.</div>
    <div>Data sources: PVMBG Badan Geologi &bull; BMKG &bull; NASA FIRMS &bull; Kemenkes RI &bull; OpenStreetMap</div>
  </div>
</body>
</html>
"""
    return html
