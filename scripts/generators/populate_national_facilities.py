"""
scripts/generators/populate_national_facilities.py

Menghasilkan basis data fasilitas publik komprehensif se-Indonesia (Seluruh 38 Provinsi)
Mencakup:
1. Sekolah (SDN, SMPN, SMAN, SMKN sebagai basis posko evakuasi BPBD)
2. Fasilitas Kesehatan (RSUP, RSUD, RS Pratama, Puskesmas Rawat Inap)
3. Bandara (Bandara Internasional, Domestik Utama, dan Bandara Perintis Nusantara)
"""

import json
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
OUT_FILE = BACKEND_DIR / "data" / "layers" / "facilities_indonesia.json"

NATIONAL_FACILITIES = [
    # =========================================================================
    # 1. BANDARA KOMERSIAL & PERINTIS LENGKAP SELURUH INDONESIA (SABANG - MERAUKE)
    # =========================================================================
    {"facility_id": "fac_air_sbx", "name": "Bandara Maimun Saleh (SBX)", "facility_type": "airport", "latitude": 5.875, "longitude": 95.340, "district": "Sabang"},
    {"facility_id": "fac_air_btj", "name": "Bandara Sultan Iskandar Muda (BTJ)", "facility_type": "airport", "latitude": 5.523, "longitude": 95.420, "district": "Aceh Besar / Banda Aceh"},
    {"facility_id": "fac_air_lsx", "name": "Bandara Malikussaleh (LSX)", "facility_type": "airport", "latitude": 5.228, "longitude": 96.951, "district": "Lhokseumawe / Aceh Utara"},
    {"facility_id": "fac_air_txx", "name": "Bandara Rembele (TXE)", "facility_type": "airport", "latitude": 4.723, "longitude": 96.852, "district": "Bener Meriah / Takengon"},
    {"facility_id": "fac_air_kno", "name": "Bandara Internasional Kualanamu (KNO)", "facility_type": "airport", "latitude": 3.642, "longitude": 98.885, "district": "Deli Serdang / Medan"},
    {"facility_id": "fac_air_mes", "name": "Bandara Soewondo (MES)", "facility_type": "airport", "latitude": 3.558, "longitude": 98.683, "district": "Medan"},
    {"facility_id": "fac_air_flz", "name": "Bandara Ferdinand Lumban Tobing (FLZ)", "facility_type": "airport", "latitude": 1.555, "longitude": 98.889, "district": "Tapanuli Tengah / Sibolga"},
    {"facility_id": "fac_air_dtb", "name": "Bandara Raja Sisingamangaraja XII (DTB)", "facility_type": "airport", "latitude": 2.259, "longitude": 98.993, "district": "Tapanuli Utara / Silangit"},
    {"facility_id": "fac_air_gns", "name": "Bandara Binaka (GNS)", "facility_type": "airport", "latitude": 1.167, "longitude": 97.705, "district": "Gunungsitoli / Nias"},
    {"facility_id": "fac_air_pdg", "name": "Bandara Internasional Minangkabau (PDG)", "facility_type": "airport", "latitude": -0.787, "longitude": 100.281, "district": "Padang Pariaman / Padang"},
    {"facility_id": "fac_air_pku", "name": "Bandara Sultan Syarif Kasim II (PKU)", "facility_type": "airport", "latitude": 0.461, "longitude": 101.444, "district": "Pekanbaru"},
    {"facility_id": "fac_air_dum", "name": "Bandara Pinang Kampai (DUM)", "facility_type": "airport", "latitude": 1.611, "longitude": 101.434, "district": "Dumai"},
    {"facility_id": "fac_air_bth", "name": "Bandara Internasional Hang Nadim (BTH)", "facility_type": "airport", "latitude": 1.121, "longitude": 104.119, "district": "Batam"},
    {"facility_id": "fac_air_tnj", "name": "Bandara Raja Haji Fisabilillah (TNJ)", "facility_type": "airport", "latitude": 0.923, "longitude": 104.532, "district": "Tanjungpinang"},
    {"facility_id": "fac_air_ntx", "name": "Bandara Raden Sadjad (NTX)", "facility_type": "airport", "latitude": 3.910, "longitude": 108.388, "district": "Natuna"},
    {"facility_id": "fac_air_djb", "name": "Bandara Sultan Thaha (DJB)", "facility_type": "airport", "latitude": -1.638, "longitude": 103.644, "district": "Kota Jambi"},
    {"facility_id": "fac_air_krj", "name": "Bandara Depati Parbo (KRC)", "facility_type": "airport", "latitude": -2.091, "longitude": 101.439, "district": "Kerinci"},
    {"facility_id": "fac_air_bks", "name": "Bandara Fatmawati Soekarno (BKS)", "facility_type": "airport", "latitude": -3.864, "longitude": 102.340, "district": "Bengkulu"},
    {"facility_id": "fac_air_plm", "name": "Bandara Sultan Mahmud Badaruddin II (PLM)", "facility_type": "airport", "latitude": -2.898, "longitude": 104.701, "district": "Palembang"},
    {"facility_id": "fac_air_pgk", "name": "Bandara Depati Amir (PGK)", "facility_type": "airport", "latitude": -2.163, "longitude": 106.139, "district": "Pangkal Pinang / Bangka"},
    {"facility_id": "fac_air_tjq", "name": "Bandara H.A.S. Hanandjoeddin (TJQ)", "facility_type": "airport", "latitude": -2.756, "longitude": 107.754, "district": "Belitung"},
    {"facility_id": "fac_air_tkg", "name": "Bandara Radin Inten II (TKG)", "facility_type": "airport", "latitude": -5.242, "longitude": 105.179, "district": "Lampung Selatan / Bandar Lampung"},
    {"facility_id": "fac_air_cgk", "name": "Bandara Internasional Soekarno-Hatta (CGK)", "facility_type": "airport", "latitude": -6.125, "longitude": 106.655, "district": "Tangerang / Banten"},
    {"facility_id": "fac_air_hlp", "name": "Bandara Halim Perdanakusuma (HLP)", "facility_type": "airport", "latitude": -6.267, "longitude": 106.891, "district": "Jakarta Timur"},
    {"facility_id": "fac_air_bdo", "name": "Bandara Husein Sastranegara (BDO)", "facility_type": "airport", "latitude": -6.900, "longitude": 107.576, "district": "Bandung"},
    {"facility_id": "fac_air_kjt", "name": "Bandara Internasional Kertajati (KJT)", "facility_type": "airport", "latitude": -6.653, "longitude": 108.232, "district": "Majalengka"},
    {"facility_id": "fac_air_cpx", "name": "Bandara Tunggul Wulung (CXP)", "facility_type": "airport", "latitude": -7.644, "longitude": 109.034, "district": "Cilacap"},
    {"facility_id": "fac_air_srg", "name": "Bandara Jenderal Ahmad Yani (SRG)", "facility_type": "airport", "latitude": -6.974, "longitude": 110.374, "district": "Semarang"},
    {"facility_id": "fac_air_soc", "name": "Bandara Adi Soemarmo (SOC)", "facility_type": "airport", "latitude": -7.516, "longitude": 110.757, "district": "Boyolali / Surakarta"},
    {"facility_id": "fac_air_yia", "name": "Bandara Internasional Yogyakarta (YIA)", "facility_type": "airport", "latitude": -7.904, "longitude": 110.057, "district": "Kulon Progo / Yogyakarta"},
    {"facility_id": "fac_air_jog", "name": "Bandara Adisutjipto (JOG)", "facility_type": "airport", "latitude": -7.788, "longitude": 110.432, "district": "Sleman / Yogyakarta"},
    {"facility_id": "fac_air_sub", "name": "Bandara Internasional Juanda (SUB)", "facility_type": "airport", "latitude": -7.379, "longitude": 112.787, "district": "Sidoarjo / Surabaya"},
    {"facility_id": "fac_air_mlg", "name": "Bandara Abdulrachman Saleh (MLG)", "facility_type": "airport", "latitude": -7.926, "longitude": 112.714, "district": "Malang"},
    {"facility_id": "fac_air_bwx", "name": "Bandara Banyuwangi (BWX)", "facility_type": "airport", "latitude": -8.309, "longitude": 114.339, "district": "Banyuwangi"},
    {"facility_id": "fac_air_dps", "name": "Bandara I Gusti Ngurah Rai (DPS)", "facility_type": "airport", "latitude": -8.748, "longitude": 115.167, "district": "Badung / Bali"},
    {"facility_id": "fac_air_lop", "name": "Bandara Lombok Praya (LOP)", "facility_type": "airport", "latitude": -8.761, "longitude": 116.275, "district": "Lombok Tengah"},
    {"facility_id": "fac_air_swq", "name": "Bandara Sultan Muhammad Kaharuddin (SWQ)", "facility_type": "airport", "latitude": -8.489, "longitude": 117.414, "district": "Sumbawa Besar"},
    {"facility_id": "fac_air_bmu", "name": "Bandara Sultan Muhammad Salahuddin (BMU)", "facility_type": "airport", "latitude": -8.539, "longitude": 118.689, "district": "Bima"},
    {"facility_id": "fac_air_lbj", "name": "Bandara Komodo (LBJ)", "facility_type": "airport", "latitude": -8.487, "longitude": 119.889, "district": "Manggarai Barat / Labuan Bajo"},
    {"facility_id": "fac_air_ene", "name": "Bandara H. Hasan Aroeboesman (ENE)", "facility_type": "airport", "latitude": -8.849, "longitude": 121.664, "district": "Ende"},
    {"facility_id": "fac_air_mof", "name": "Bandara Frans Seda (MOF)", "facility_type": "airport", "latitude": -8.625, "longitude": 122.238, "district": "Sikka / Maumere"},
    {"facility_id": "fac_air_lka", "name": "Bandara Gewayantana (LKA)", "facility_type": "airport", "latitude": -8.275, "longitude": 123.010, "district": "Flores Timur / Larantuka"},
    {"facility_id": "fac_air_lwb", "name": "Bandara Wunopito (LWE)", "facility_type": "airport", "latitude": -8.356, "longitude": 123.511, "district": "Lembata"},
    {"facility_id": "fac_air_ard", "name": "Bandara Mali (ARD)", "facility_type": "airport", "latitude": -8.217, "longitude": 124.571, "district": "Alor"},
    {"facility_id": "fac_air_tmc", "name": "Bandara Tambolaka (TMC)", "facility_type": "airport", "latitude": -9.409, "longitude": 119.243, "district": "Sumba Barat Daya"},
    {"facility_id": "fac_air_wgp", "name": "Bandara Umbu Mehang Kunda (WGP)", "facility_type": "airport", "latitude": -9.667, "longitude": 120.301, "district": "Sumba Timur / Waingapu"},
    {"facility_id": "fac_air_koe", "name": "Bandara El Tari (KOE)", "facility_type": "airport", "latitude": -10.171, "longitude": 123.670, "district": "Kupang"},
    {"facility_id": "fac_air_pnk", "name": "Bandara Supadio (PNK)", "facility_type": "airport", "latitude": -0.150, "longitude": 109.403, "district": "Kubu Raya / Pontianak"},
    {"facility_id": "fac_air_ktg", "name": "Bandara Rahadi Oesman (KTG)", "facility_type": "airport", "latitude": -1.816, "longitude": 109.963, "district": "Ketapang"},
    {"facility_id": "fac_air_sqg", "name": "Bandara Tebelian (SQG)", "facility_type": "airport", "latitude": 0.052, "longitude": 111.455, "district": "Sintang"},
    {"facility_id": "fac_air_pku_kalteng", "name": "Bandara Tjilik Riwut (PKY)", "facility_type": "airport", "latitude": -2.225, "longitude": 113.945, "district": "Palangka Raya"},
    {"facility_id": "fac_air_smq", "name": "Bandara H. Asan Sampit (SMQ)", "facility_type": "airport", "latitude": -2.500, "longitude": 112.975, "district": "Kotawaringin Timur / Sampit"},
    {"facility_id": "fac_air_pkn", "name": "Bandara Iskandar (PKN)", "facility_type": "airport", "latitude": -2.705, "longitude": 111.674, "district": "Kotawaringin Barat / Pangkalan Bun"},
    {"facility_id": "fac_air_bdj", "name": "Bandara Internasional Syamsudin Noor (BDJ)", "facility_type": "airport", "latitude": -3.442, "longitude": 114.757, "district": "Banjarbaru / Banjarmasin"},
    {"facility_id": "fac_air_bpn", "name": "Bandara Sultan Aji Muhammad Sulaiman Sepinggan (BPN)", "facility_type": "airport", "latitude": -1.268, "longitude": 116.894, "district": "Balikpapan"},
    {"facility_id": "fac_air_smd", "name": "Bandara Aji Pangeran Tumenggung Pranoto (AAP)", "facility_type": "airport", "latitude": -0.374, "longitude": 117.258, "district": "Samarinda"},
    {"facility_id": "fac_air_beo", "name": "Bandara Kalimarau (BEJ)", "facility_type": "airport", "latitude": 2.155, "longitude": 117.432, "district": "Berau"},
    {"facility_id": "fac_air_trk", "name": "Bandara Juwata (TRK)", "facility_type": "airport", "latitude": 3.327, "longitude": 117.568, "district": "Tarakan"},
    {"facility_id": "fac_air_upg", "name": "Bandara Sultan Hasanuddin (UPG)", "facility_type": "airport", "latitude": -5.061, "longitude": 119.554, "district": "Maros / Makassar"},
    {"facility_id": "fac_air_mju", "name": "Bandara Tampa Padang (MJU)", "facility_type": "airport", "latitude": -2.597, "longitude": 119.030, "district": "Mamuju"},
    {"facility_id": "fac_air_plw", "name": "Bandara Mutiara SIS Al-Jufri (PLW)", "facility_type": "airport", "latitude": -0.918, "longitude": 119.909, "district": "Palu"},
    {"facility_id": "fac_air_luw", "name": "Bandara Syukuran Aminuddin Amir (LUW)", "facility_type": "airport", "latitude": -1.039, "longitude": 122.774, "district": "Banggai / Luwuk"},
    {"facility_id": "fac_air_kdi", "name": "Bandara Haluoleo (KDI)", "facility_type": "airport", "latitude": -4.082, "longitude": 122.418, "district": "Konawe Selatan / Kendari"},
    {"facility_id": "fac_air_gto", "name": "Bandara Djalaluddin (GTO)", "facility_type": "airport", "latitude": 0.637, "longitude": 122.852, "district": "Gorontalo"},
    {"facility_id": "fac_air_mdc", "name": "Bandara Internasional Sam Ratulangi (MDC)", "facility_type": "airport", "latitude": 1.549, "longitude": 124.926, "district": "Manado"},
    {"facility_id": "fac_air_nah", "name": "Bandara Naha (NAH)", "facility_type": "airport", "latitude": 3.682, "longitude": 125.529, "district": "Kepulauan Sangihe"},
    {"facility_id": "fac_air_tte", "name": "Bandara Sultan Babullah (TTE)", "facility_type": "airport", "latitude": 0.831, "longitude": 127.381, "district": "Ternate"},
    {"facility_id": "fac_air_kaz", "name": "Bandara Kuabang Kao (KAZ)", "facility_type": "airport", "latitude": 1.190, "longitude": 127.905, "district": "Halmahera Utara / Tobelo"},
    {"facility_id": "fac_air_amq", "name": "Bandara Pattimura (AMQ)", "facility_type": "airport", "latitude": -3.708, "longitude": 128.089, "district": "Ambon"},
    {"facility_id": "fac_air_lah", "name": "Bandara Oesman Sadik (LAH)", "facility_type": "airport", "latitude": -0.636, "longitude": 127.482, "district": "Halmahera Selatan / Labuha"},
    {"facility_id": "fac_air_tua", "name": "Bandara Karel Sadsuitubun (LUV)", "facility_type": "airport", "latitude": -5.760, "longitude": 132.748, "district": "Maluku Tenggara / Langgur / Tual"},
    {"facility_id": "fac_air_soq", "name": "Bandara Domine Eduard Osok (SOQ)", "facility_type": "airport", "latitude": -0.925, "longitude": 131.287, "district": "Sorong"},
    {"facility_id": "fac_air_mkw", "name": "Bandara Rendani (MKW)", "facility_type": "airport", "latitude": -0.891, "longitude": 134.050, "district": "Manokwari"},
    {"facility_id": "fac_air_nbx", "name": "Bandara Douw Aturure (NBX)", "facility_type": "airport", "latitude": -3.367, "longitude": 135.497, "district": "Nabire"},
    {"facility_id": "fac_air_tim", "name": "Bandara Mozes Kilangin (TIM)", "facility_type": "airport", "latitude": -4.528, "longitude": 136.887, "district": "Mimika / Timika"},
    {"facility_id": "fac_air_bik", "name": "Bandara Frans Kaisiepo (BIK)", "facility_type": "airport", "latitude": -1.190, "longitude": 136.108, "district": "Biak Numfor"},
    {"facility_id": "fac_air_djj", "name": "Bandara Sentani (DJJ)", "facility_type": "airport", "latitude": -2.576, "longitude": 140.516, "district": "Jayapura"},
    {"facility_id": "fac_air_wmx", "name": "Bandara Wamena (WMX)", "facility_type": "airport", "latitude": -4.098, "longitude": 138.956, "district": "Jayawijaya / Wamena"},
    {"facility_id": "fac_air_mkq", "name": "Bandara Mopah (MKQ)", "facility_type": "airport", "latitude": -8.520, "longitude": 140.418, "district": "Merauke"},

    # =========================================================================
    # 2. FASILITAS KESEHATAN (RSUD, RSUP, PUSKESMAS UTAMA SE-INDONESIA)
    # =========================================================================
    # Aceh & Sumut
    {"facility_id": "fac_hc_aceh_01", "name": "RSUD dr. Zainoel Abidin", "facility_type": "healthcare", "latitude": 5.568, "longitude": 95.340, "district": "Banda Aceh"},
    {"facility_id": "fac_hc_aceh_02", "name": "RSUD Datu Beru Takengon", "facility_type": "healthcare", "latitude": 4.625, "longitude": 96.845, "district": "Aceh Tengah"},
    {"facility_id": "fac_hc_aceh_03", "name": "Puskesmas Lampahan", "facility_type": "healthcare", "latitude": 4.810, "longitude": 96.790, "district": "Bener Meriah"},
    {"facility_id": "fac_hc_sumut_01", "name": "RSUP H. Adam Malik Medan", "facility_type": "healthcare", "latitude": 3.518, "longitude": 98.607, "district": "Medan"},
    {"facility_id": "fac_hc_sumut_02", "name": "RSUD Kabanjahe (Sinabung Area)", "facility_type": "healthcare", "latitude": 3.178, "longitude": 98.495, "district": "Karo"},
    {"facility_id": "fac_hc_sumut_03", "name": "Puskesmas Naman Teran (Sinabung)", "facility_type": "healthcare", "latitude": 3.195, "longitude": 98.410, "district": "Karo"},
    {"facility_id": "fac_hc_sumut_04", "name": "Puskesmas Simpang Empat Karo", "facility_type": "healthcare", "latitude": 3.170, "longitude": 98.445, "district": "Karo"},
    {"facility_id": "fac_hc_sumut_05", "name": "RSUD dr. Djasamen Saragih", "facility_type": "healthcare", "latitude": 2.955, "longitude": 99.060, "district": "Pematangsiantar"},

    # Sumatera Barat & Riau & Kepri
    {"facility_id": "fac_hc_sumbar_01", "name": "RSUP Dr. M. Djamil Padang", "facility_type": "healthcare", "latitude": -0.941, "longitude": 100.366, "district": "Padang"},
    {"facility_id": "fac_hc_sumbar_02", "name": "RSUD Dr. Achmad Mochtar Bukittinggi (Marapi Area)", "facility_type": "healthcare", "latitude": -0.305, "longitude": 100.370, "district": "Bukittinggi"},
    {"facility_id": "fac_hc_sumbar_03", "name": "RSUD Padang Panjang (Marapi Area)", "facility_type": "healthcare", "latitude": -0.470, "longitude": 100.410, "district": "Padang Panjang"},
    {"facility_id": "fac_hc_sumbar_04", "name": "Puskesmas Sungai Pua (Kaki G. Marapi)", "facility_type": "healthcare", "latitude": -0.360, "longitude": 100.420, "district": "Agam"},
    {"facility_id": "fac_hc_sumbar_05", "name": "Puskesmas Canduang (Kaki G. Marapi)", "facility_type": "healthcare", "latitude": -0.315, "longitude": 100.445, "district": "Agam"},
    {"facility_id": "fac_hc_sumbar_06", "name": "RSUD M. Zein Painan", "facility_type": "healthcare", "latitude": -1.350, "longitude": 100.575, "district": "Pesisir Selatan"},
    {"facility_id": "fac_hc_riau_01", "name": "RSUD Arifin Achmad", "facility_type": "healthcare", "latitude": 0.528, "longitude": 101.450, "district": "Pekanbaru"},
    {"facility_id": "fac_hc_riau_02", "name": "RSUD Selasih Pangkalan Kerinci (Tesso Nilo)", "facility_type": "healthcare", "latitude": 0.395, "longitude": 101.865, "district": "Pelalawan"},
    {"facility_id": "fac_hc_riau_03", "name": "Puskesmas Ukui (Zona Buffer TN Tesso Nilo)", "facility_type": "healthcare", "latitude": -0.195, "longitude": 101.990, "district": "Pelalawan"},
    {"facility_id": "fac_hc_riau_04", "name": "RSUD Tengku Rafi'an Siak (Giam Siak)", "facility_type": "healthcare", "latitude": 0.795, "longitude": 102.045, "district": "Siak"},
    {"facility_id": "fac_hc_riau_05", "name": "Puskesmas Bukit Batu (Giam Siak Kecil)", "facility_type": "healthcare", "latitude": 1.485, "longitude": 101.810, "district": "Bengkalis"},
    {"facility_id": "fac_hc_kepri_01", "name": "RSBP Batam", "facility_type": "healthcare", "latitude": 1.125, "longitude": 104.010, "district": "Batam"},
    {"facility_id": "fac_hc_kepri_02", "name": "RSUD Raja Ahmad Tabib", "facility_type": "healthcare", "latitude": 0.935, "longitude": 104.495, "district": "Tanjungpinang"},

    # Jambi, Bengkulu, Sumsel, Lampung
    {"facility_id": "fac_hc_jambi_01", "name": "RSUD Raden Mattaher", "facility_type": "healthcare", "latitude": -1.595, "longitude": 103.605, "district": "Kota Jambi"},
    {"facility_id": "fac_hc_jambi_02", "name": "RSUD Nurdin Hamzah (TN Berbak Area)", "facility_type": "healthcare", "latitude": -1.155, "longitude": 103.840, "district": "Tanjung Jabung Timur"},
    {"facility_id": "fac_hc_jambi_03", "name": "Puskesmas Nipah Panjang (Pesisir TN Berbak)", "facility_type": "healthcare", "latitude": -1.280, "longitude": 104.200, "district": "Tanjung Jabung Timur"},
    {"facility_id": "fac_hc_jambi_04", "name": "RSUD Mayjen H.A. Thalib Sungai Penuh (Kerinci)", "facility_type": "healthcare", "latitude": -2.060, "longitude": 101.390, "district": "Sungai Penuh / Kerinci"},
    {"facility_id": "fac_hc_bengkulu_01", "name": "RSUD M. Yunus Bengkulu", "facility_type": "healthcare", "latitude": -3.830, "longitude": 102.305, "district": "Kota Bengkulu"},
    {"facility_id": "fac_hc_bengkulu_02", "name": "RSUD Curup (G. Kaba Area)", "facility_type": "healthcare", "latitude": -3.465, "longitude": 102.520, "district": "Rejang Lebong"},
    {"facility_id": "fac_hc_sumsel_01", "name": "RSUP Dr. Mohammad Hoesin", "facility_type": "healthcare", "latitude": -2.965, "longitude": 104.750, "district": "Palembang"},
    {"facility_id": "fac_hc_sumsel_02", "name": "RSUD Kayuagung (Padang Sugihan Gambut)", "facility_type": "healthcare", "latitude": -3.395, "longitude": 104.855, "district": "Ogan Komering Ilir"},
    {"facility_id": "fac_hc_sumsel_03", "name": "Puskesmas Tulung Selapan (Gambut Karhutla)", "facility_type": "healthcare", "latitude": -3.220, "longitude": 105.350, "district": "Ogan Komering Ilir"},
    {"facility_id": "fac_hc_sumsel_04", "name": "RSUD Besemah Pagar Alam (G. Dempo Area)", "facility_type": "healthcare", "latitude": -4.030, "longitude": 103.250, "district": "Pagar Alam"},
    {"facility_id": "fac_hc_lampung_01", "name": "RSUD Dr. H. Abdul Moeloek", "facility_type": "healthcare", "latitude": -5.4050, "longitude": 105.2600, "district": "Bandar Lampung"},
    {"facility_id": "fac_hc_lampung_02", "name": "RSUD Bob Bazar Kalianda (Krakatau Area)", "facility_type": "healthcare", "latitude": -5.7285, "longitude": 105.5945, "district": "Lampung Selatan"},
    {"facility_id": "fac_hc_lampung_03", "name": "Puskesmas Rawat Inap Rajabasa (Krakatau Area)", "facility_type": "healthcare", "latitude": -5.8250, "longitude": 105.6050, "district": "Lampung Selatan"},
    {"facility_id": "fac_hc_lampung_04", "name": "RSUD Sukadana (TN Way Kambas Area)", "facility_type": "healthcare", "latitude": -5.0800, "longitude": 105.5450, "district": "Lampung Timur"},
    {"facility_id": "fac_hc_lampung_05", "name": "Puskesmas Way Jepara (Buffer Way Kambas)", "facility_type": "healthcare", "latitude": -5.1950, "longitude": 105.6700, "district": "Lampung Timur"},
    {"facility_id": "fac_hc_lampung_sidomulyo", "name": "Puskesmas Rawat Inap Sidomulyo (Rujukan Bebas Abu)", "facility_type": "healthcare", "latitude": -5.5450, "longitude": 105.5245, "district": "Lampung Selatan"},

    # Banten, DKI, Jawa Barat
    {"facility_id": "fac_hc_banten_01", "name": "RSUD Banten", "facility_type": "healthcare", "latitude": -6.1536, "longitude": 106.1421, "district": "Serang"},
    {"facility_id": "fac_hc_banten_02", "name": "RSUD Berkah Pandeglang (Krakatau & Ujung Kulon)", "facility_type": "healthcare", "latitude": -6.3150, "longitude": 106.1080, "district": "Pandeglang"},
    {"facility_id": "fac_hc_banten_03", "name": "Puskesmas Labuan (Pesisir Selat Sunda)", "facility_type": "healthcare", "latitude": -6.3815, "longitude": 105.8345, "district": "Pandeglang"},
    {"facility_id": "fac_hc_banten_04", "name": "Puskesmas Sumur (Zona Ujung Kulon / Krakatau)", "facility_type": "healthcare", "latitude": -6.6515, "longitude": 105.5925, "district": "Pandeglang"},
    {"facility_id": "fac_hc_banten_cilegon", "name": "RSUD Cilegon (Zona Bebas Abu Selat Sunda)", "facility_type": "healthcare", "latitude": -6.0180, "longitude": 106.0520, "district": "Cilegon"},
    {"facility_id": "fac_hc_dki_01", "name": "RSCM (RSUP Nasional Dr. Cipto Mangunkusumo)", "facility_type": "healthcare", "latitude": -6.197, "longitude": 106.848, "district": "Jakarta Pusat"},
    {"facility_id": "fac_hc_dki_02", "name": "RSPI Prof. Dr. Sulianti Saroso", "facility_type": "healthcare", "latitude": -6.128, "longitude": 106.865, "district": "Jakarta Utara"},
    {"facility_id": "fac_hc_dki_03", "name": "RSUP Persahabatan (Pusat Respirasi Nasional)", "facility_type": "healthcare", "latitude": -6.208, "longitude": 106.885, "district": "Jakarta Timur"},
    {"facility_id": "fac_hc_jabar_01", "name": "RSUP Dr. Hasan Sadikin", "facility_type": "healthcare", "latitude": -6.896, "longitude": 107.598, "district": "Bandung"},
    {"facility_id": "fac_hc_jabar_02", "name": "RSUD Lembang (Tangkuban Parahu Area)", "facility_type": "healthcare", "latitude": -6.820, "longitude": 107.620, "district": "Bandung Barat"},
    {"facility_id": "fac_hc_jabar_03", "name": "Puskesmas Ciater (Kaki G. Tangkuban Parahu)", "facility_type": "healthcare", "latitude": -6.745, "longitude": 107.660, "district": "Subang"},
    {"facility_id": "fac_hc_jabar_04", "name": "RSUD Cimacan (G. Gede-Pangrango Area)", "facility_type": "healthcare", "latitude": -6.745, "longitude": 107.025, "district": "Cianjur"},
    {"facility_id": "fac_hc_jabar_05", "name": "RSUD Sekarwangi Cibadak (G. Salak Area)", "facility_type": "healthcare", "latitude": -6.905, "longitude": 106.785, "district": "Sukabumi"},
    {"facility_id": "fac_hc_jabar_06", "name": "RSUD dr. Slamet Garut (G. Guntur & Papandayan)", "facility_type": "healthcare", "latitude": -7.215, "longitude": 107.895, "district": "Garut"},
    {"facility_id": "fac_hc_jabar_07", "name": "RSUD 45 Kuningan (G. Ciremai Area)", "facility_type": "healthcare", "latitude": -6.980, "longitude": 108.485, "district": "Kuningan"},
    {"facility_id": "fac_hc_jabar_08", "name": "RSUD dr. Soekardjo Tasikmalaya (G. Galunggung)", "facility_type": "healthcare", "latitude": -7.335, "longitude": 108.220, "district": "Tasikmalaya"},

    # Jawa Tengah & D.I. Yogyakarta
    {"facility_id": "fac_hc_jateng_01", "name": "RSUP Dr. Kariadi Semarang", "facility_type": "healthcare", "latitude": -6.995, "longitude": 110.408, "district": "Semarang"},
    {"facility_id": "fac_hc_jateng_02", "name": "RSUD Pandan Arang Boyolali (G. Merapi & Merbabu)", "facility_type": "healthcare", "latitude": -7.535, "longitude": 110.595, "district": "Boyolali"},
    {"facility_id": "fac_hc_jateng_03", "name": "Puskesmas Selo (Antara Merapi & Merbabu)", "facility_type": "healthcare", "latitude": -7.505, "longitude": 110.468, "district": "Boyolali"},
    {"facility_id": "fac_hc_jateng_04", "name": "RSUD Muntilan (Merapi Jalur Abu Barat)", "facility_type": "healthcare", "latitude": -7.580, "longitude": 110.295, "district": "Magelang"},
    {"facility_id": "fac_hc_jateng_05", "name": "Puskesmas Dukun (KRB III G. Merapi)", "facility_type": "healthcare", "latitude": -7.545, "longitude": 110.340, "district": "Magelang"},
    {"facility_id": "fac_hc_jateng_06", "name": "RSUD Prof. Dr. Margono Soekarjo (G. Slamet)", "facility_type": "healthcare", "latitude": -7.445, "longitude": 109.255, "district": "Banyumas / Purwokerto"},
    {"facility_id": "fac_hc_jateng_07", "name": "RSUD Karanganyar (Kaki G. Lawu)", "facility_type": "healthcare", "latitude": -7.595, "longitude": 110.950, "district": "Karanganyar"},
    {"facility_id": "fac_hc_jateng_08", "name": "RSUD KRT Setjonegoro Wonosobo (Dieng Area)", "facility_type": "healthcare", "latitude": -7.360, "longitude": 109.905, "district": "Wonosobo"},
    {"facility_id": "fac_hc_diy_01", "name": "RSUP Dr. Sardjito", "facility_type": "healthcare", "latitude": -7.768, "longitude": 110.373, "district": "Sleman / Yogyakarta"},
    {"facility_id": "fac_hc_diy_02", "name": "RS Panti Nugroho Pakem (Evakuasi Merapi)", "facility_type": "healthcare", "latitude": -7.668, "longitude": 110.418, "district": "Sleman"},
    {"facility_id": "fac_hc_diy_03", "name": "Puskesmas Cangkringan (KRB III G. Merapi)", "facility_type": "healthcare", "latitude": -7.648, "longitude": 110.458, "district": "Sleman"},
    {"facility_id": "fac_hc_diy_04", "name": "RSUD Sleman Murangan", "facility_type": "healthcare", "latitude": -7.685, "longitude": 110.335, "district": "Sleman"},

    # Jawa Timur
    {"facility_id": "fac_hc_jatim_01", "name": "RSUD Dr. Soetomo Surabaya", "facility_type": "healthcare", "latitude": -7.268, "longitude": 112.758, "district": "Surabaya"},
    {"facility_id": "fac_hc_jatim_02", "name": "RSUD Dr. Saiful Anwar Malang", "facility_type": "healthcare", "latitude": -7.973, "longitude": 112.632, "district": "Malang"},
    {"facility_id": "fac_hc_jatim_03", "name": "RSUD Dr. Haryoto Lumajang (G. Semeru Area)", "facility_type": "healthcare", "latitude": -8.130, "longitude": 113.220, "district": "Lumajang"},
    {"facility_id": "fac_hc_jatim_04", "name": "RSUD Pasirian (Evakuasi Semeru)", "facility_type": "healthcare", "latitude": -8.215, "longitude": 113.110, "district": "Lumajang"},
    {"facility_id": "fac_hc_jatim_05", "name": "Puskesmas Pronojiwo (Zona Terdampak Lahar/Abu Semeru)", "facility_type": "healthcare", "latitude": -8.212, "longitude": 112.915, "district": "Lumajang"},
    {"facility_id": "fac_hc_jatim_06", "name": "Puskesmas Candipuro (Zona Terdampak Semeru)", "facility_type": "healthcare", "latitude": -8.195, "longitude": 113.045, "district": "Lumajang"},
    {"facility_id": "fac_hc_jatim_07", "name": "RSUD Tongas Probolinggo (G. Bromo Area)", "facility_type": "healthcare", "latitude": -7.740, "longitude": 113.110, "district": "Probolinggo"},
    {"facility_id": "fac_hc_jatim_08", "name": "Puskesmas Sukapura (Kaki G. Bromo)", "facility_type": "healthcare", "latitude": -7.890, "longitude": 113.010, "district": "Probolinggo"},
    {"facility_id": "fac_hc_jatim_09", "name": "RSUD Simpang Lima Gumul Kediri (G. Kelud Area)", "facility_type": "healthcare", "latitude": -7.810, "longitude": 112.060, "district": "Kediri"},
    {"facility_id": "fac_hc_jatim_10", "name": "RSUD Blambangan Banyuwangi (Ijen & Raung)", "facility_type": "healthcare", "latitude": -8.205, "longitude": 114.370, "district": "Banyuwangi"},
    {"facility_id": "fac_hc_jatim_11", "name": "Puskesmas Licin (Kaki G. Ijen Banyuwangi)", "facility_type": "healthcare", "latitude": -8.200, "longitude": 114.280, "district": "Banyuwangi"},

    # Bali & Nusa Tenggara
    {"facility_id": "fac_hc_bali_01", "name": "RSUP Prof. Dr. I.G.N.G. Ngoerah (Sanglah)", "facility_type": "healthcare", "latitude": -8.675, "longitude": 115.210, "district": "Denpasar"},
    {"facility_id": "fac_hc_bali_02", "name": "RSUD Karangasem (G. Agung Area)", "facility_type": "healthcare", "latitude": -8.455, "longitude": 115.610, "district": "Karangasem"},
    {"facility_id": "fac_hc_bali_03", "name": "Puskesmas Rendang (KRB III G. Agung)", "facility_type": "healthcare", "latitude": -8.450, "longitude": 115.430, "district": "Karangasem"},
    {"facility_id": "fac_hc_bali_04", "name": "RSUD Bangli (G. Batur Area)", "facility_type": "healthcare", "latitude": -8.455, "longitude": 115.355, "district": "Bangli"},
    {"facility_id": "fac_hc_bali_05", "name": "Puskesmas Kintamani I (Kaldera G. Batur)", "facility_type": "healthcare", "latitude": -8.250, "longitude": 115.335, "district": "Bangli"},
    {"facility_id": "fac_hc_ntb_01", "name": "RSUD Provinsi NTB", "facility_type": "healthcare", "latitude": -8.610, "longitude": 116.120, "district": "Mataram"},
    {"facility_id": "fac_hc_ntb_02", "name": "RSUD dr. R. Soedjono Selong (G. Rinjani Area)", "facility_type": "healthcare", "latitude": -8.650, "longitude": 116.535, "district": "Lombok Timur"},
    {"facility_id": "fac_hc_ntb_03", "name": "Puskesmas Sembalun (Lembah Kaldera Rinjani)", "facility_type": "healthcare", "latitude": -8.365, "longitude": 116.535, "district": "Lombok Timur"},
    {"facility_id": "fac_hc_ntb_04", "name": "RSUD Dompu (G. Tambora Area)", "facility_type": "healthcare", "latitude": -8.535, "longitude": 118.460, "district": "Dompu"},
    {"facility_id": "fac_hc_ntb_05", "name": "Puskesmas Calabai Pekat (Kaki G. Tambora)", "facility_type": "healthcare", "latitude": -8.210, "longitude": 117.910, "district": "Dompu"},
    {"facility_id": "fac_hc_ntt_01", "name": "RSUD Prof. Dr. W.Z. Johannes Kupang", "facility_type": "healthcare", "latitude": -10.165, "longitude": 123.590, "district": "Kupang"},
    {"facility_id": "fac_hc_ntt_02", "name": "RSUD dr. Hendrikus Fernandez Larantuka (G. Lewotobi)", "facility_type": "healthcare", "latitude": -8.340, "longitude": 122.980, "district": "Flores Timur"},
    {"facility_id": "fac_hc_ntt_03", "name": "Puskesmas Boru Wulanggitang (Kaki Lewotobi Laki-laki)", "facility_type": "healthcare", "latitude": -8.542, "longitude": 122.775, "district": "Flores Timur"},
    {"facility_id": "fac_hc_ntt_04", "name": "RSUD TC Hillers Maumere (G. Egon Area)", "facility_type": "healthcare", "latitude": -8.625, "longitude": 122.215, "district": "Sikka"},
    {"facility_id": "fac_hc_ntt_05", "name": "RSUD Ende (G. Kelimutu Area)", "facility_type": "healthcare", "latitude": -8.840, "longitude": 121.655, "district": "Ende"},
    {"facility_id": "fac_hc_ntt_06", "name": "RSUD Lewoleba (G. Ili Lewotolok)", "facility_type": "healthcare", "latitude": -8.365, "longitude": 123.525, "district": "Lembata"},
    {"facility_id": "fac_hc_ntt_07", "name": "RSUD Komodo Labuan Bajo", "facility_type": "healthcare", "latitude": -8.510, "longitude": 119.895, "district": "Manggarai Barat"},

    # Kalimantan (Zona Karhutla Gambut & Hutan)
    {"facility_id": "fac_hc_kalteng_01", "name": "RSUD Doris Sylvanus Palangka Raya (TN Sebangau)", "facility_type": "healthcare", "latitude": -2.210, "longitude": 113.922, "district": "Palangka Raya"},
    {"facility_id": "fac_hc_kalteng_02", "name": "RSUD dr. Murjani Sampit (Karhutla Kotim)", "facility_type": "healthcare", "latitude": -2.530, "longitude": 112.960, "district": "Kotawaringin Timur"},
    {"facility_id": "fac_hc_kalteng_03", "name": "RSUD Sultan Imanuddin Pangkalan Bun (TN Tanjung Puting)", "facility_type": "healthcare", "latitude": -2.685, "longitude": 111.625, "district": "Kotawaringin Barat"},
    {"facility_id": "fac_hc_kalteng_04", "name": "Puskesmas Kereng Bangkirai (Pintu Masuk TN Sebangau)", "facility_type": "healthcare", "latitude": -2.285, "longitude": 113.880, "district": "Palangka Raya"},
    {"facility_id": "fac_hc_kalteng_05", "name": "RSUD Pulang Pisau (Eks PLG Gambut)", "facility_type": "healthcare", "latitude": -2.750, "longitude": 114.255, "district": "Pulang Pisau"},
    {"facility_id": "fac_hc_kalteng_06", "name": "RSUD dr. H. Soemarno Sosroatmodjo (Kuala Kapuas / PLG)", "facility_type": "healthcare", "latitude": -3.010, "longitude": 114.385, "district": "Kapuas"},
    {"facility_id": "fac_hc_kalsel_01", "name": "RSUD Ulin Banjarmasin", "facility_type": "healthcare", "latitude": -3.325, "longitude": 114.605, "district": "Banjarmasin"},
    {"facility_id": "fac_hc_kalsel_02", "name": "RSUD Idaman Banjarbaru (Karhutla Banjarbaru)", "facility_type": "healthcare", "latitude": -3.450, "longitude": 114.825, "district": "Banjarbaru"},
    {"facility_id": "fac_hc_kalsel_03", "name": "RSUD Ratu Zalecha Martapura", "facility_type": "healthcare", "latitude": -3.420, "longitude": 114.860, "district": "Banjar"},
    {"facility_id": "fac_hc_kalsel_04", "name": "RSUD H. Hasan Basry Kandangan (Pegunungan Meratus)", "facility_type": "healthcare", "latitude": -2.785, "longitude": 115.265, "district": "Hulu Sungai Selatan"},
    {"facility_id": "fac_hc_kalsel_05", "name": "Puskesmas Loksado (Jantung Pegunungan Meratus)", "facility_type": "healthcare", "latitude": -2.795, "longitude": 115.420, "district": "Hulu Sungai Selatan"},
    {"facility_id": "fac_hc_kalbar_01", "name": "RSUD dr. Soedarso Pontianak", "facility_type": "healthcare", "latitude": -0.060, "longitude": 109.355, "district": "Pontianak"},
    {"facility_id": "fac_hc_kalbar_02", "name": "RSUD Dr. Agoesdjam Ketapang (TN Gunung Palung)", "facility_type": "healthcare", "latitude": -1.835, "longitude": 109.975, "district": "Ketapang"},
    {"facility_id": "fac_hc_kalbar_03", "name": "RSUD Achmad Diponegoro Putussibau (Danau Sentarum)", "facility_type": "healthcare", "latitude": 0.855, "longitude": 112.925, "district": "Kapuas Hulu"},
    {"facility_id": "fac_hc_kaltim_01", "name": "RSUD Abdoel Wahab Sjahranie Samarinda", "facility_type": "healthcare", "latitude": -0.485, "longitude": 117.140, "district": "Samarinda"},
    {"facility_id": "fac_hc_kaltim_02", "name": "RSUD Dr. Kanujoso Djatiwibowo Balikpapan (H.L. Sungai Wain)", "facility_type": "healthcare", "latitude": -1.225, "longitude": 116.865, "district": "Balikpapan"},
    {"facility_id": "fac_hc_kaltim_03", "name": "RSUD Ratu Aji Putri Botung (Nusantara IKN Area)", "facility_type": "healthcare", "latitude": -1.315, "longitude": 116.690, "district": "Penajam Paser Utara"},
    {"facility_id": "fac_hc_kaltim_04", "name": "RSUD Kudungga Sangatta (TN Kutai Area)", "facility_type": "healthcare", "latitude": 0.510, "longitude": 117.550, "district": "Kutai Timur"},
    {"facility_id": "fac_hc_kaltara_01", "name": "RSUD dr. H. Soemarno Sosroatmodjo Tanjung Selor", "facility_type": "healthcare", "latitude": 2.845, "longitude": 117.365, "district": "Bulungan"},
    {"facility_id": "fac_hc_kaltara_02", "name": "RSUD Kota Tarakan", "facility_type": "healthcare", "latitude": 3.310, "longitude": 117.595, "district": "Tarakan"},

    # Sulawesi
    {"facility_id": "fac_hc_sulsel_01", "name": "RSUP Dr. Wahidin Sudirohusodo Makassar", "facility_type": "healthcare", "latitude": -5.135, "longitude": 119.495, "district": "Makassar"},
    {"facility_id": "fac_hc_sulsel_02", "name": "RSUD Dr. La Palaloi Maros (Bantimurung Area)", "facility_type": "healthcare", "latitude": -5.010, "longitude": 119.575, "district": "Maros"},
    {"facility_id": "fac_hc_sulsel_03", "name": "RSUD Syekh Yusuf Gowa (G. Bawakaraeng Area)", "facility_type": "healthcare", "latitude": -5.205, "longitude": 119.455, "district": "Gowa"},
    {"facility_id": "fac_hc_sulut_01", "name": "RSUP Prof. Dr. R.D. Kandou Manado", "facility_type": "healthcare", "latitude": 1.455, "longitude": 124.830, "district": "Manado"},
    {"facility_id": "fac_hc_sulut_02", "name": "RSUD Tagulandang (Gunung Ruang Area)", "facility_type": "healthcare", "latitude": 2.285, "longitude": 125.420, "district": "Kep. Sitaro"},
    {"facility_id": "fac_hc_sulut_03", "name": "Puskesmas Minanga Tagulandang (Evakuasi G. Ruang)", "facility_type": "healthcare", "latitude": 2.295, "longitude": 125.435, "district": "Kep. Sitaro"},
    {"facility_id": "fac_hc_sulut_04", "name": "RSUD Anugerah Tomohon (G. Lokon & Mahawu)", "facility_type": "healthcare", "latitude": 1.330, "longitude": 124.845, "district": "Tomohon"},
    {"facility_id": "fac_hc_sulut_05", "name": "RSUD Noongan Minahasa (G. Soputan Area)", "facility_type": "healthcare", "latitude": 1.130, "longitude": 124.785, "district": "Minahasa"},
    {"facility_id": "fac_hc_sulteng_01", "name": "RSUD Undata Palu", "facility_type": "healthcare", "latitude": -0.885, "longitude": 119.890, "district": "Palu"},
    {"facility_id": "fac_hc_sulteng_02", "name": "RSUD Torabelo Sigi (TN Lore Lindu Area)", "facility_type": "healthcare", "latitude": -0.995, "longitude": 119.920, "district": "Sigi"},
    {"facility_id": "fac_hc_sultra_01", "name": "RSUD Bahteramas Kendari", "facility_type": "healthcare", "latitude": -4.015, "longitude": 122.525, "district": "Kendari"},
    {"facility_id": "fac_hc_gorontalo_01", "name": "RSUD Prof. Dr. H. Aloei Saboe", "facility_type": "healthcare", "latitude": 0.555, "longitude": 123.080, "district": "Kota Gorontalo"},

    # Maluku & Papua
    {"facility_id": "fac_hc_malut_01", "name": "RSUD Dr. H. Chasan Boesoirie Ternate (G. Gamalama)", "facility_type": "healthcare", "latitude": 0.795, "longitude": 127.380, "district": "Ternate"},
    {"facility_id": "fac_hc_malut_02", "name": "Puskesmas Gamkonora (G. Ibu Area)", "facility_type": "healthcare", "latitude": 1.460, "longitude": 127.575, "district": "Halmahera Barat"},
    {"facility_id": "fac_hc_malut_03", "name": "RSUD Tobelo (G. Dukono Area)", "facility_type": "healthcare", "latitude": 1.728, "longitude": 128.002, "district": "Halmahera Utara"},
    {"facility_id": "fac_hc_maluku_01", "name": "RSUP Dr. J. Leimena Ambon", "facility_type": "healthcare", "latitude": -3.655, "longitude": 128.185, "district": "Ambon"},
    {"facility_id": "fac_hc_maluku_02", "name": "RSUD Banda Neira (G. Banda Api Area)", "facility_type": "healthcare", "latitude": -4.525, "longitude": 129.905, "district": "Maluku Tengah"},
    {"facility_id": "fac_hc_papua_01", "name": "RSUD Dok II Jayapura", "facility_type": "healthcare", "latitude": -2.535, "longitude": 140.710, "district": "Jayapura"},
    {"facility_id": "fac_hc_papua_02", "name": "RSUD Yowari Sentani", "facility_type": "healthcare", "latitude": -2.565, "longitude": 140.485, "district": "Jayapura"},
    {"facility_id": "fac_hc_papua_03", "name": "RSUD Sele Be Solu Sorong", "facility_type": "healthcare", "latitude": -0.890, "longitude": 131.305, "district": "Sorong"},
    {"facility_id": "fac_hc_papua_04", "name": "RSUD Kabupaten Mimika Timika", "facility_type": "healthcare", "latitude": -4.545, "longitude": 136.885, "district": "Mimika"},
    {"facility_id": "fac_hc_papua_05", "name": "RSUD Wamena (Pegunungan Tengah)", "facility_type": "healthcare", "latitude": -4.095, "longitude": 138.945, "district": "Jayawijaya"},
    {"facility_id": "fac_hc_papua_06", "name": "RSUD Merauke (TN Wasur Area)", "facility_type": "healthcare", "latitude": -8.490, "longitude": 140.405, "district": "Merauke"},

    # =========================================================================
    # 3. SEKOLAH NEGERI STRATEGIS & BASIS POSKO EVAKUASI BPBD SE-INDONESIA
    # =========================================================================
    # Sumatera
    {"facility_id": "fac_sch_aceh_01", "name": "SMAN 1 Banda Aceh", "facility_type": "school", "latitude": 5.550, "longitude": 95.320, "district": "Banda Aceh"},
    {"facility_id": "fac_sch_aceh_02", "name": "SMAN 1 Takengon (G. Bur Ni Telong Area)", "facility_type": "school", "latitude": 4.630, "longitude": 96.840, "district": "Aceh Tengah"},
    {"facility_id": "fac_sch_sumut_01", "name": "SMAN 1 Medan", "facility_type": "school", "latitude": 3.585, "longitude": 98.665, "district": "Medan"},
    {"facility_id": "fac_sch_sumut_02", "name": "SMAN 1 Berastagi (Sinabung & Sibayak Area)", "facility_type": "school", "latitude": 3.185, "longitude": 98.505, "district": "Karo"},
    {"facility_id": "fac_sch_sumut_03", "name": "SMPN 1 Simpang Empat (Posko Erupsi Sinabung)", "facility_type": "school", "latitude": 3.175, "longitude": 98.440, "district": "Karo"},
    {"facility_id": "fac_sch_sumbar_01", "name": "SMAN 1 Bukittinggi (G. Marapi & Singgalang)", "facility_type": "school", "latitude": -0.305, "longitude": 100.365, "district": "Bukittinggi"},
    {"facility_id": "fac_sch_sumbar_02", "name": "SMAN 1 Padang Panjang (Kaki Marapi)", "facility_type": "school", "latitude": -0.465, "longitude": 100.405, "district": "Padang Panjang"},
    {"facility_id": "fac_sch_sumbar_03", "name": "SMPN 1 Canduang (Jalur Evakuasi Marapi)", "facility_type": "school", "latitude": -0.320, "longitude": 100.450, "district": "Agam"},
    {"facility_id": "fac_sch_riau_01", "name": "SMAN 1 Pekanbaru", "facility_type": "school", "latitude": 0.525, "longitude": 101.445, "district": "Pekanbaru"},
    {"facility_id": "fac_sch_riau_02", "name": "SMAN 1 Pangkalan Kerinci (TN Tesso Nilo)", "facility_type": "school", "latitude": 0.390, "longitude": 101.860, "district": "Pelalawan"},
    {"facility_id": "fac_sch_riau_03", "name": "SMPN 1 Ukui (Buffer TN Tesso Nilo)", "facility_type": "school", "latitude": -0.190, "longitude": 101.995, "district": "Pelalawan"},
    {"facility_id": "fac_sch_riau_04", "name": "SMAN 1 Siak (Giam Siak Kecil)", "facility_type": "school", "latitude": 0.790, "longitude": 102.040, "district": "Siak"},
    {"facility_id": "fac_sch_jambi_01", "name": "SMAN 1 Kota Jambi", "facility_type": "school", "latitude": -1.605, "longitude": 103.610, "district": "Kota Jambi"},
    {"facility_id": "fac_sch_jambi_02", "name": "SMAN 1 Muara Sabak (TN Berbak)", "facility_type": "school", "latitude": -1.150, "longitude": 103.845, "district": "Tanjung Jabung Timur"},
    {"facility_id": "fac_sch_jambi_03", "name": "SMAN 1 Kayu Aro (Kaki Gunung Kerinci)", "facility_type": "school", "latitude": -1.785, "longitude": 101.275, "district": "Kerinci"},
    {"facility_id": "fac_sch_sumsel_01", "name": "SMAN 1 Palembang", "facility_type": "school", "latitude": -2.975, "longitude": 104.745, "district": "Palembang"},
    {"facility_id": "fac_sch_sumsel_02", "name": "SMAN 1 Kayuagung (Lahan Gambut Padang Sugihan)", "facility_type": "school", "latitude": -3.390, "longitude": 104.850, "district": "Ogan Komering Ilir"},
    {"facility_id": "fac_sch_sumsel_03", "name": "SMAN 1 Pagar Alam (Kaki Gunung Dempo)", "facility_type": "school", "latitude": -4.025, "longitude": 103.255, "district": "Pagar Alam"},
    {"facility_id": "fac_sch_lampung_01", "name": "SMAN 1 Kalianda (Anak Krakatau)", "facility_type": "school", "latitude": -5.7315, "longitude": 105.5965, "district": "Lampung Selatan"},
    {"facility_id": "fac_sch_lampung_02", "name": "SMPN 1 Rajabasa (Pesisir Selat Sunda Krakatau)", "facility_type": "school", "latitude": -5.8280, "longitude": 105.6080, "district": "Lampung Selatan"},
    {"facility_id": "fac_sch_lampung_03", "name": "SMAN 1 Way Jepara (TN Way Kambas)", "facility_type": "school", "latitude": -5.1900, "longitude": 105.6650, "district": "Lampung Timur"},
    {"facility_id": "fac_sch_lampung_bakauheni", "name": "SMAN 1 Bakauheni (Krakatau Area)", "facility_type": "school", "latitude": -5.8645, "longitude": 105.7515, "district": "Lampung Selatan"},

    # Banten, DKI, Jawa Barat
    {"facility_id": "fac_sch_banten_01", "name": "SMK Negeri 1 Labuan (Krakatau Evacuation)", "facility_type": "school", "latitude": -6.3765, "longitude": 105.8340, "district": "Pandeglang"},
    {"facility_id": "fac_sch_banten_02", "name": "SDN Sumur 01 (Zona Ujung Kulon)", "facility_type": "school", "latitude": -6.6520, "longitude": 105.5913, "district": "Pandeglang"},
    {"facility_id": "fac_sch_banten_03", "name": "SMAN 1 Anyer (Pesisir Selat Sunda)", "facility_type": "school", "latitude": -6.0530, "longitude": 105.9321, "district": "Serang"},
    {"facility_id": "fac_sch_dki_01", "name": "SMAN 68 Jakarta", "facility_type": "school", "latitude": -6.192, "longitude": 106.848, "district": "Jakarta Pusat"},
    {"facility_id": "fac_sch_dki_02", "name": "SMAN 8 Jakarta", "facility_type": "school", "latitude": -6.225, "longitude": 106.855, "district": "Jakarta Selatan"},
    {"facility_id": "fac_sch_jabar_01", "name": "SMAN 1 Lembang (G. Tangkuban Parahu)", "facility_type": "school", "latitude": -6.815, "longitude": 107.615, "district": "Bandung Barat"},
    {"facility_id": "fac_sch_jabar_02", "name": "SMPN 1 Ciater (Kaki Tangkuban Parahu)", "facility_type": "school", "latitude": -6.740, "longitude": 107.665, "district": "Subang"},
    {"facility_id": "fac_sch_jabar_03", "name": "SMAN 1 Cipanas (G. Gede-Pangrango)", "facility_type": "school", "latitude": -6.740, "longitude": 107.030, "district": "Cianjur"},
    {"facility_id": "fac_sch_jabar_04", "name": "SMAN 1 Cisurupan (Kaki G. Papandayan)", "facility_type": "school", "latitude": -7.315, "longitude": 107.795, "district": "Garut"},
    {"facility_id": "fac_sch_jabar_05", "name": "SMAN 1 Cilimus (Kaki G. Ciremai)", "facility_type": "school", "latitude": -6.885, "longitude": 108.495, "district": "Kuningan"},

    # Jawa Tengah & DIY
    {"facility_id": "fac_sch_jateng_01", "name": "SMAN 1 Pakem (Posko Utama Pengungsian Merapi)", "facility_type": "school", "latitude": -7.665, "longitude": 110.420, "district": "Sleman"},
    {"facility_id": "fac_sch_jateng_02", "name": "SMPN 1 Cangkringan (KRB III G. Merapi)", "facility_type": "school", "latitude": -7.640, "longitude": 110.460, "district": "Sleman"},
    {"facility_id": "fac_sch_jateng_03", "name": "SDN Glagaharjo (KRB III G. Merapi)", "facility_type": "school", "latitude": -7.610, "longitude": 110.470, "district": "Sleman"},
    {"facility_id": "fac_sch_jateng_04", "name": "SMPN 1 Selo (Antara Merapi & Merbabu)", "facility_type": "school", "latitude": -7.502, "longitude": 110.465, "district": "Boyolali"},
    {"facility_id": "fac_sch_jateng_05", "name": "SMAN 1 Dukun (Jalur Evakuasi Merapi Magelang)", "facility_type": "school", "latitude": -7.540, "longitude": 110.335, "district": "Magelang"},
    {"facility_id": "fac_sch_jateng_06", "name": "SMAN 1 Baturaden (Kaki G. Slamet)", "facility_type": "school", "latitude": -7.350, "longitude": 109.225, "district": "Banyumas"},
    {"facility_id": "fac_sch_jateng_07", "name": "SMAN 1 Kejajar (Kawasan Vulkanik Dataran Tinggi Dieng)", "facility_type": "school", "latitude": -7.265, "longitude": 109.915, "district": "Wonosobo"},
    {"facility_id": "fac_sch_jateng_08", "name": "SMAN 1 Tawangmangu (Kaki G. Lawu)", "facility_type": "school", "latitude": -7.665, "longitude": 111.135, "district": "Karanganyar"},

    # Jawa Timur
    {"facility_id": "fac_sch_jatim_01", "name": "SMAN 1 Candipuro (Jalur Evakuasi Semeru)", "facility_type": "school", "latitude": -8.190, "longitude": 113.040, "district": "Lumajang"},
    {"facility_id": "fac_sch_jatim_02", "name": "SMPN 1 Pronojiwo (KRB Semeru)", "facility_type": "school", "latitude": -8.210, "longitude": 112.910, "district": "Lumajang"},
    {"facility_id": "fac_sch_jatim_03", "name": "SDN Supiturang 01 (Zona Terdampak Awan Panas Semeru)", "facility_type": "school", "latitude": -8.205, "longitude": 112.985, "district": "Lumajang"},
    {"facility_id": "fac_sch_jatim_04", "name": "SMPN 1 Sukapura (Tengger Bromo)", "facility_type": "school", "latitude": -7.885, "longitude": 113.015, "district": "Probolinggo"},
    {"facility_id": "fac_sch_jatim_05", "name": "SMAN 1 Ngancar (Kaki G. Kelud Kediri)", "facility_type": "school", "latitude": -7.940, "longitude": 112.165, "district": "Kediri"},
    {"facility_id": "fac_sch_jatim_06", "name": "SMPN 1 Licin (Kaki G. Ijen Banyuwangi)", "facility_type": "school", "latitude": -8.195, "longitude": 114.285, "district": "Banyuwangi"},
    {"facility_id": "fac_sch_jatim_07", "name": "SMAN 1 Banyuputih (TN Baluran Area)", "facility_type": "school", "latitude": -7.835, "longitude": 114.325, "district": "Situbondo"},

    # Bali & Nusa Tenggara
    {"facility_id": "fac_sch_bali_01", "name": "SMAN 1 Selat (KRB G. Agung)", "facility_type": "school", "latitude": -8.440, "longitude": 115.480, "district": "Karangasem"},
    {"facility_id": "fac_sch_bali_02", "name": "SMPN 1 Rendang (Posko Pengungsian G. Agung)", "facility_type": "school", "latitude": -8.445, "longitude": 115.425, "district": "Karangasem"},
    {"facility_id": "fac_sch_bali_03", "name": "SMPN 1 Kintamani (Kaldera G. Batur)", "facility_type": "school", "latitude": -8.245, "longitude": 115.340, "district": "Bangli"},
    {"facility_id": "fac_sch_ntb_01", "name": "SMAN 1 Sembalun (Lembah G. Rinjani)", "facility_type": "school", "latitude": -8.360, "longitude": 116.530, "district": "Lombok Timur"},
    {"facility_id": "fac_sch_ntb_02", "name": "SMPN 1 Bayan Senaru (Kaki Rinjani Utara)", "facility_type": "school", "latitude": -8.265, "longitude": 116.425, "district": "Lombok Utara"},
    {"facility_id": "fac_sch_ntb_03", "name": "SMAN 1 Pekat (Kaki G. Tambora)", "facility_type": "school", "latitude": -8.215, "longitude": 117.915, "district": "Dompu"},
    {"facility_id": "fac_sch_ntt_01", "name": "SMP Negeri 1 Wulanggitang (KRB G. Lewotobi)", "facility_type": "school", "latitude": -8.545, "longitude": 122.780, "district": "Flores Timur"},
    {"facility_id": "fac_sch_ntt_02", "name": "SMAN 1 Ilebura (Kaki G. Lewotobi Laki-laki)", "facility_type": "school", "latitude": -8.560, "longitude": 122.810, "district": "Flores Timur"},
    {"facility_id": "fac_sch_ntt_03", "name": "SDK Hokeng (Zona Terdampak Erupsi Lewotobi)", "facility_type": "school", "latitude": -8.535, "longitude": 122.755, "district": "Flores Timur"},
    {"facility_id": "fac_sch_ntt_04", "name": "SMAN 1 Ile Ape (Kaki G. Ili Lewotolok)", "facility_type": "school", "latitude": -8.310, "longitude": 123.550, "district": "Lembata"},
    {"facility_id": "fac_sch_ntt_05", "name": "SMPN 1 Kelimutu (Kaki G. Kelimutu Danau 3 Warna)", "facility_type": "school", "latitude": -8.765, "longitude": 121.820, "district": "Ende"},

    # Kalimantan
    {"facility_id": "fac_sch_kalteng_01", "name": "SMAN 1 Palangka Raya (TN Sebangau)", "facility_type": "school", "latitude": -2.215, "longitude": 113.918, "district": "Palangka Raya"},
    {"facility_id": "fac_sch_kalteng_02", "name": "SMPN 2 Palangka Raya", "facility_type": "school", "latitude": -2.205, "longitude": 113.925, "district": "Palangka Raya"},
    {"facility_id": "fac_sch_kalteng_03", "name": "SMAN 1 Sampit (Zona Karhutla Kotim)", "facility_type": "school", "latitude": -2.535, "longitude": 112.955, "district": "Kotawaringin Timur"},
    {"facility_id": "fac_sch_kalteng_04", "name": "SMAN 1 Pangkalan Bun (TN Tanjung Puting)", "facility_type": "school", "latitude": -2.680, "longitude": 111.620, "district": "Kotawaringin Barat"},
    {"facility_id": "fac_sch_kalteng_05", "name": "SMPN 1 Kumai (Gerbang Masuk TN Tanjung Puting)", "facility_type": "school", "latitude": -2.740, "longitude": 111.735, "district": "Kotawaringin Barat"},
    {"facility_id": "fac_sch_kalteng_06", "name": "SMAN 1 Pulang Pisau (Eks PLG Gambut)", "facility_type": "school", "latitude": -2.745, "longitude": 114.260, "district": "Pulang Pisau"},
    {"facility_id": "fac_sch_kalsel_01", "name": "SMAN 1 Banjarbaru (Episentrum Karhutla Kalsel)", "facility_type": "school", "latitude": -3.440, "longitude": 114.830, "district": "Banjarbaru"},
    {"facility_id": "fac_sch_kalsel_02", "name": "SMAN 2 Banjarbaru (Gambut Bandara Syamsudin Noor)", "facility_type": "school", "latitude": -3.455, "longitude": 114.795, "district": "Banjarbaru"},
    {"facility_id": "fac_sch_kalsel_03", "name": "SMAN 1 Kandangan (Pegunungan Meratus)", "facility_type": "school", "latitude": -2.790, "longitude": 115.260, "district": "Hulu Sungai Selatan"},
    {"facility_id": "fac_sch_kalsel_04", "name": "SMPN 1 Loksado (Masyarakat Adat Dayak Meratus)", "facility_type": "school", "latitude": -2.790, "longitude": 115.425, "district": "Hulu Sungai Selatan"},
    {"facility_id": "fac_sch_kalbar_01", "name": "SMAN 1 Pontianak", "facility_type": "school", "latitude": -0.045, "longitude": 109.340, "district": "Pontianak"},
    {"facility_id": "fac_sch_kalbar_02", "name": "SMAN 1 Sukadana (TN Gunung Palung)", "facility_type": "school", "latitude": -1.240, "longitude": 109.955, "district": "Kayong Utara"},
    {"facility_id": "fac_sch_kalbar_03", "name": "SMAN 1 Ketapang (TN Gunung Palung Selatan)", "facility_type": "school", "latitude": -1.840, "longitude": 109.970, "district": "Ketapang"},
    {"facility_id": "fac_sch_kalbar_04", "name": "SMAN 1 Batang Lupar Lanjak (TN Danau Sentarum)", "facility_type": "school", "latitude": 0.985, "longitude": 112.145, "district": "Kapuas Hulu"},
    {"facility_id": "fac_sch_kaltim_01", "name": "SMAN 1 Balikpapan (Hutan Lindung Sungai Wain)", "facility_type": "school", "latitude": -1.255, "longitude": 116.835, "district": "Balikpapan"},
    {"facility_id": "fac_sch_kaltim_02", "name": "SMAN 8 Balikpapan (Kawasan H.L. S. Wain Utara)", "facility_type": "school", "latitude": -1.175, "longitude": 116.870, "district": "Balikpapan"},
    {"facility_id": "fac_sch_kaltim_03", "name": "SMAN 1 Sepaku (Ibu Kota Nusantara / IKN)", "facility_type": "school", "latitude": -0.915, "longitude": 116.780, "district": "Penajam Paser Utara"},
    {"facility_id": "fac_sch_kaltim_04", "name": "SMAN 1 Bontang (TN Kutai Area)", "facility_type": "school", "latitude": 0.135, "longitude": 117.485, "district": "Bontang"},

    # Sulawesi
    {"facility_id": "fac_sch_sulut_01", "name": "SMAN 1 Tagulandang (Evakuasi G. Ruang)", "facility_type": "school", "latitude": 2.290, "longitude": 125.410, "district": "Kep. Sitaro"},
    {"facility_id": "fac_sch_sulut_02", "name": "SMPN 1 Tagulandang (G. Ruang Area)", "facility_type": "school", "latitude": 2.280, "longitude": 125.415, "district": "Kep. Sitaro"},
    {"facility_id": "fac_sch_sulut_03", "name": "SMAN 1 Tomohon (Kaki G. Lokon & Mahawu)", "facility_type": "school", "latitude": 1.325, "longitude": 124.840, "district": "Tomohon"},
    {"facility_id": "fac_sch_sulut_04", "name": "SMAN 1 Silian Raya (Kaki G. Soputan)", "facility_type": "school", "latitude": 1.075, "longitude": 124.715, "district": "Minahasa Tenggara"},
    {"facility_id": "fac_sch_sulut_05", "name": "SMAN 1 Tahuna (Kaki G. Awu Sangihe)", "facility_type": "school", "latitude": 3.610, "longitude": 125.495, "district": "Kepulauan Sangihe"},
    {"facility_id": "fac_sch_sulteng_01", "name": "SMAN 1 Palu", "facility_type": "school", "latitude": -0.895, "longitude": 119.875, "district": "Palu"},
    {"facility_id": "fac_sch_sulteng_02", "name": "SMAN 1 Kulawi (TN Lore Lindu)", "facility_type": "school", "latitude": -1.445, "longitude": 119.980, "district": "Sigi"},
    {"facility_id": "fac_sch_sulsel_01", "name": "SMAN 1 Maros (TN Bantimurung Bulusaraung)", "facility_type": "school", "latitude": -5.005, "longitude": 119.570, "district": "Maros"},
    {"facility_id": "fac_sch_sulsel_02", "name": "SMAN 1 Tinggimoncong Malino (G. Bawakaraeng)", "facility_type": "school", "latitude": -5.255, "longitude": 119.855, "district": "Gowa"},

    # Maluku & Papua
    {"facility_id": "fac_sch_malut_01", "name": "SMAN 1 Ternate (Kaki G. Gamalama)", "facility_type": "school", "latitude": 0.790, "longitude": 127.375, "district": "Ternate"},
    {"facility_id": "fac_sch_malut_02", "name": "SMAN 1 Ibu (Zona Erupsi G. Ibu)", "facility_type": "school", "latitude": 1.455, "longitude": 127.580, "district": "Halmahera Barat"},
    {"facility_id": "fac_sch_malut_03", "name": "SMPN 2 Ibu Utara (KRB G. Ibu)", "facility_type": "school", "latitude": 1.510, "longitude": 127.605, "district": "Halmahera Barat"},
    {"facility_id": "fac_sch_malut_04", "name": "SMAN 1 Tobelo (Kaki G. Dukono)", "facility_type": "school", "latitude": 1.730, "longitude": 128.005, "district": "Halmahera Utara"},
    {"facility_id": "fac_sch_malut_05", "name": "SMPN 1 Tobelo (Jalur Abu G. Dukono)", "facility_type": "school", "latitude": 1.725, "longitude": 127.995, "district": "Halmahera Utara"},
    {"facility_id": "fac_sch_maluku_01", "name": "SMAN 1 Ambon", "facility_type": "school", "latitude": -3.695, "longitude": 128.180, "district": "Ambon"},
    {"facility_id": "fac_sch_maluku_02", "name": "SMAN 1 Banda (Pulau G. Banda Api)", "facility_type": "school", "latitude": -4.520, "longitude": 129.900, "district": "Maluku Tengah"},
    {"facility_id": "fac_sch_papua_01", "name": "SMAN 1 Jayapura", "facility_type": "school", "latitude": -2.535, "longitude": 140.705, "district": "Jayapura"},
    {"facility_id": "fac_sch_papua_02", "name": "SMAN 1 Sentani", "facility_type": "school", "latitude": -2.560, "longitude": 140.510, "district": "Jayapura"},
    {"facility_id": "fac_sch_papua_03", "name": "SMAN 1 Timika (Kaki Pegunungan Sudirman Carstensz)", "facility_type": "school", "latitude": -4.540, "longitude": 136.880, "district": "Mimika"},
    {"facility_id": "fac_sch_papua_04", "name": "SMAN 1 Wamena (Lembah Baliem / Lorentz)", "facility_type": "school", "latitude": -4.090, "longitude": 138.940, "district": "Jayawijaya"},
    {"facility_id": "fac_sch_papua_05", "name": "SMAN 1 Merauke (TN Wasur Area)", "facility_type": "school", "latitude": -8.495, "longitude": 140.410, "district": "Merauke"},
    {"facility_id": "fac_sch_papua_06", "name": "SMPN 1 Sota Merauke (Perbatasan RI-PNG di TN Wasur)", "facility_type": "school", "latitude": -8.455, "longitude": 141.020, "district": "Merauke"}
]

def main():
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(NATIONAL_FACILITIES, f, indent=2, ensure_ascii=False)

    counts = {}
    for item in NATIONAL_FACILITIES:
        t = item["facility_type"]
        counts[t] = counts.get(t, 0) + 1

    print(f"Berhasil menghasilkan {len(NATIONAL_FACILITIES)} fasilitas publik nasional di {OUT_FILE}:")
    for k, v in counts.items():
        print(f"  - {k}: {v} unit")

if __name__ == "__main__":
    main()
