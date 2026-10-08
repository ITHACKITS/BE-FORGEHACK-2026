"""
scripts/generate_all_volcanoes_geojson.py

Menghasilkan katalog spasial lengkap 70 Gunung Api Aktif PVMBG se-Indonesia
(Mencakup seluruh gunung api Tipe A dari Sumatera, Jawa, Bali, NTB, NTT, Maluku, hingga Sulawesi)
"""

import json
from pathlib import Path

ALL_VOLCANOES = [
    # --- SUMATERA (13) ---
    {
        "id": "seulawah_agam", "name": "G. Seulawah Agam", "province": "Aceh",
        "elevation_m": 1810, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Aktivitas kawah normal", "coords": [95.658, 5.448], "region": "Sumatera"
    },
    {
        "id": "peuet_sago", "name": "G. Peuet Sago", "province": "Pidie, Aceh",
        "elevation_m": 2801, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 2.0, "last_vona": "Aktivitas fumarola tenang", "coords": [96.329, 4.914], "region": "Sumatera"
    },
    {
        "id": "burni_telong", "name": "G. Burni Telong", "province": "Bener Meriah, Aceh",
        "elevation_m": 2624, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Aktivitas kawah normal", "coords": [96.821, 4.773], "region": "Sumatera"
    },
    {
        "id": "sinabung", "name": "G. Sinabung", "province": "Karo, Sumatera Utara",
        "elevation_m": 2460, "level": 2, "level_name": "Level II (Waspada)", "color": "#eab308",
        "radius_bahaya_km": 3.0, "last_vona": "Emisi asap kawah putih sedang", "coords": [98.392, 3.170], "region": "Sumatera"
    },
    {
        "id": "sibayak", "name": "G. Sibayak", "province": "Karo, Sumatera Utara",
        "elevation_m": 2212, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.0, "last_vona": "Aktivitas solfatara normal", "coords": [98.520, 3.230], "region": "Sumatera"
    },
    {
        "id": "sorikmarapi", "name": "G. Sorikmarapi", "province": "Mandailing Natal, Sumatera Utara",
        "elevation_m": 2145, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Aktivitas kawah normal", "coords": [99.622, 0.686], "region": "Sumatera"
    },
    {
        "id": "marapi_sumatera", "name": "G. Marapi", "province": "Sumatera Barat",
        "elevation_m": 2891, "level": 3, "level_name": "Level III (Siaga)", "color": "#f97316",
        "radius_bahaya_km": 4.5, "last_vona": "Erupsi eksplosif kolom abu 2000m", "coords": [100.473, -0.381], "region": "Sumatera"
    },
    {
        "id": "tandikat", "name": "G. Tandikat", "province": "Padang Pariaman, Sumatera Barat",
        "elevation_m": 2438, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Aktivitas normal", "coords": [100.317, -0.433], "region": "Sumatera"
    },
    {
        "id": "talang", "name": "G. Talang", "province": "Solok, Sumatera Barat",
        "elevation_m": 2597, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Emisi asap kawah tipis", "coords": [100.679, -0.978], "region": "Sumatera"
    },
    {
        "id": "kerinci", "name": "G. Kerinci", "province": "Jambi / Sumatera Barat",
        "elevation_m": 3805, "level": 2, "level_name": "Level II (Waspada)", "color": "#eab308",
        "radius_bahaya_km": 3.0, "last_vona": "Emisi gas sulfatara kelabu 600m", "coords": [101.264, -1.697], "region": "Sumatera"
    },
    {
        "id": "kaba", "name": "G. Kaba", "province": "Rejang Lebong, Bengkulu",
        "elevation_m": 1952, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Aktivitas kawah normal", "coords": [102.620, -3.520], "region": "Sumatera"
    },
    {
        "id": "dempo", "name": "G. Dempo", "province": "Pagar Alam, Sumatera Selatan",
        "elevation_m": 3173, "level": 2, "level_name": "Level II (Waspada)", "color": "#eab308",
        "radius_bahaya_km": 2.5, "last_vona": "Erupsi freatik kawah merapi", "coords": [103.130, -4.030], "region": "Sumatera"
    },
    {
        "id": "anak_krakatau_2026_09", "name": "G. Anak Krakatau", "province": "Selat Sunda / Lampung",
        "elevation_m": 157, "level": 3, "level_name": "Level III (Siaga)", "color": "#f97316",
        "radius_bahaya_km": 5.0, "last_vona": "Erupsi abu vulkanik tinggi 15.200m ASL", "coords": [105.423, -6.102], "region": "Sumatera"
    },

    # --- JAWA (19) ---
    {
        "id": "salak", "name": "G. Salak", "province": "Sukabumi / Bogor, Jawa Barat",
        "elevation_m": 2211, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.0, "last_vona": "Kawah Ratu aktif normal", "coords": [106.733, -6.717], "region": "Jawa"
    },
    {
        "id": "gede", "name": "G. Gede", "province": "Cianjur / Bogor, Jawa Barat",
        "elevation_m": 2958, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.0, "last_vona": "Aktivitas kawah normal", "coords": [106.983, -6.783], "region": "Jawa"
    },
    {
        "id": "tangkuban_parahu", "name": "G. Tangkuban Parahu", "province": "Bandung Barat, Jawa Barat",
        "elevation_m": 2084, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Kawah Ratu normal terbuka", "coords": [107.600, -6.770], "region": "Jawa"
    },
    {
        "id": "guntur", "name": "G. Guntur", "province": "Garut, Jawa Barat",
        "elevation_m": 2249, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Aktivitas kawah normal", "coords": [107.840, -7.143], "region": "Jawa"
    },
    {
        "id": "papandayan", "name": "G. Papandayan", "province": "Garut, Jawa Barat",
        "elevation_m": 2665, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Emisi asap solfatara normal", "coords": [107.730, -7.320], "region": "Jawa"
    },
    {
        "id": "galunggung", "name": "G. Galunggung", "province": "Tasikmalaya, Jawa Barat",
        "elevation_m": 2168, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.0, "last_vona": "Kawah danau tenang", "coords": [108.058, -7.250], "region": "Jawa"
    },
    {
        "id": "ciremai", "name": "G. Ciremai", "province": "Kuningan / Majalengka, Jawa Barat",
        "elevation_m": 3078, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Aktivitas kawah puncak normal", "coords": [108.400, -6.892], "region": "Jawa"
    },
    {
        "id": "slamet", "name": "G. Slamet", "province": "Banyumas / Brebes, Jawa Tengah",
        "elevation_m": 3432, "level": 2, "level_name": "Level II (Waspada)", "color": "#eab308",
        "radius_bahaya_km": 2.0, "last_vona": "Peningkatan kegempaan tremor hembusan", "coords": [109.208, -7.242], "region": "Jawa"
    },
    {
        "id": "dieng", "name": "G. Dieng", "province": "Banjarnegara / Wonosobo, Jawa Tengah",
        "elevation_m": 2565, "level": 2, "level_name": "Level II (Waspada)", "color": "#eab308",
        "radius_bahaya_km": 1.0, "last_vona": "Waspada gas beracun CO2 Kawah Timbang", "coords": [109.900, -7.200], "region": "Jawa"
    },
    {
        "id": "sundoro", "name": "G. Sindoro", "province": "Temanggung / Wonosobo, Jawa Tengah",
        "elevation_m": 3151, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.0, "last_vona": "Aktivitas kawah puncak normal", "coords": [109.992, -7.300], "region": "Jawa"
    },
    {
        "id": "sumbing", "name": "G. Sumbing", "province": "Magelang / Temanggung, Jawa Tengah",
        "elevation_m": 3371, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.0, "last_vona": "Aktivitas normal", "coords": [110.070, -7.384], "region": "Jawa"
    },
    {
        "id": "merapi_yogyakarta", "name": "G. Merapi", "province": "Sleman / Klaten / Boyolali / Magelang",
        "elevation_m": 2968, "level": 3, "level_name": "Level III (Siaga)", "color": "#f97316",
        "radius_bahaya_km": 7.0, "last_vona": "Guguran lava dan awan panas Kali Krasak", "coords": [110.446, -7.540], "region": "Jawa"
    },
    {
        "id": "kelud", "name": "G. Kelud", "province": "Kediri / Blitar, Jawa Timur",
        "elevation_m": 1731, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Normal pasca erupsi besar 2014", "coords": [112.308, -7.930], "region": "Jawa"
    },
    {
        "id": "arjuno_welirang", "name": "G. Arjuno-Welirang", "province": "Malang / Pasuruan, Jawa Timur",
        "elevation_m": 3339, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Aktivitas solfatara normal", "coords": [112.580, -7.725], "region": "Jawa"
    },
    {
        "id": "bromo", "name": "G. Bromo", "province": "Probolinggo / Pasuruan, Jawa Timur",
        "elevation_m": 2329, "level": 2, "level_name": "Level II (Waspada)", "color": "#eab308",
        "radius_bahaya_km": 1.0, "last_vona": "Aktivitas hembusan kawah aktif", "coords": [112.950, -7.942], "region": "Jawa"
    },
    {
        "id": "semeru", "name": "G. Semeru", "province": "Lumajang / Malang, Jawa Timur",
        "elevation_m": 3676, "level": 3, "level_name": "Level III (Siaga)", "color": "#f97316",
        "radius_bahaya_km": 5.0, "last_vona": "Aktivitas APG menerus Besuk Kobokan", "coords": [112.922, -8.108], "region": "Jawa"
    },
    {
        "id": "lamongan", "name": "G. Lamongan", "province": "Lumajang, Jawa Timur",
        "elevation_m": 1651, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.0, "last_vona": "Aktivitas normal", "coords": [113.342, -7.979], "region": "Jawa"
    },
    {
        "id": "raung", "name": "G. Raung", "province": "Banyuwangi / Bondowoso, Jawa Timur",
        "elevation_m": 3332, "level": 2, "level_name": "Level II (Waspada)", "color": "#eab308",
        "radius_bahaya_km": 3.0, "last_vona": "Gempa tremor hembusan menerus", "coords": [114.042, -8.125], "region": "Jawa"
    },
    {
        "id": "ijen", "name": "G. Ijen", "province": "Banyuwangi / Bondowoso, Jawa Timur",
        "elevation_m": 2386, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Danau kawah asam aktif normal", "coords": [114.242, -8.058], "region": "Jawa"
    },

    # --- BALI & NUSA TENGGARA BARAT (5) ---
    {
        "id": "batur", "name": "G. Batur", "province": "Bangli, Bali",
        "elevation_m": 1717, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.0, "last_vona": "Aktivitas kawah normal", "coords": [115.375, -8.242], "region": "Bali & Nusa Tenggara"
    },
    {
        "id": "agung", "name": "G. Agung", "province": "Karangasem, Bali",
        "elevation_m": 3142, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 2.0, "last_vona": "Aktivitas vulkanik normal pasca 2017", "coords": [115.508, -8.343], "region": "Bali & Nusa Tenggara"
    },
    {
        "id": "rinjani", "name": "G. Rinjani", "province": "Lombok Timur, Nusa Tenggara Barat",
        "elevation_m": 3726, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Segara Anak dan Barujari normal", "coords": [116.458, -8.420], "region": "Bali & Nusa Tenggara"
    },
    {
        "id": "tambora", "name": "G. Tambora", "province": "Dompu / Bima, Nusa Tenggara Barat",
        "elevation_m": 2851, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 2.0, "last_vona": "Kaldera raksasa aktif normal", "coords": [118.000, -8.250], "region": "Bali & Nusa Tenggara"
    },
    {
        "id": "sangeang_api", "name": "G. Sangeang Api", "province": "Bima, Nusa Tenggara Barat",
        "elevation_m": 1949, "level": 2, "level_name": "Level II (Waspada)", "color": "#eab308",
        "radius_bahaya_km": 1.5, "last_vona": "Emisi asap kawah Doro Api", "coords": [119.070, -8.200], "region": "Bali & Nusa Tenggara"
    },

    # --- NUSA TENGGARA TIMUR (13) ---
    {
        "id": "rokatenda", "name": "G. Rokatenda (Paluweh)", "province": "Sikka, Nusa Tenggara Timur",
        "elevation_m": 875, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Aktivitas kawah normal", "coords": [121.708, -8.320], "region": "Bali & Nusa Tenggara"
    },
    {
        "id": "ebulobo", "name": "G. Ebulobo", "province": "Nagekeo, Nusa Tenggara Timur",
        "elevation_m": 2124, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Aktivitas normal", "coords": [121.200, -8.823], "region": "Bali & Nusa Tenggara"
    },
    {
        "id": "inielika", "name": "G. Inielika", "province": "Ngada, Nusa Tenggara Timur",
        "elevation_m": 1559, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.0, "last_vona": "Aktivitas normal", "coords": [120.980, -8.730], "region": "Bali & Nusa Tenggara"
    },
    {
        "id": "kelimutu", "name": "G. Kelimutu", "province": "Ende, Nusa Tenggara Timur",
        "elevation_m": 1639, "level": 2, "level_name": "Level II (Waspada)", "color": "#eab308",
        "radius_bahaya_km": 1.5, "last_vona": "Perubahan warna dan suhu Danau Kawah", "coords": [121.820, -8.770], "region": "Bali & Nusa Tenggara"
    },
    {
        "id": "iya", "name": "G. Iya", "province": "Ende, Nusa Tenggara Timur",
        "elevation_m": 637, "level": 3, "level_name": "Level III (Siaga)", "color": "#f97316",
        "radius_bahaya_km": 3.0, "last_vona": "Peningkatan kegempaan vulkanik dalam", "coords": [121.645, -8.897], "region": "Bali & Nusa Tenggara"
    },
    {
        "id": "egon", "name": "G. Egon", "province": "Sikka, Nusa Tenggara Timur",
        "elevation_m": 1703, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Aktivitas kawah normal", "coords": [122.450, -8.670], "region": "Bali & Nusa Tenggara"
    },
    {
        "id": "lewotobi_laki_laki", "name": "G. Lewotobi Laki-laki", "province": "Flores Timur, Nusa Tenggara Timur",
        "elevation_m": 1584, "level": 4, "level_name": "Level IV (Awas)", "color": "#ef4444",
        "radius_bahaya_km": 7.0, "last_vona": "Erupsi paroksimal kolom abu 8.000m", "coords": [122.768, -8.538], "region": "Bali & Nusa Tenggara"
    },
    {
        "id": "lewotobi_perempuan", "name": "G. Lewotobi Perempuan", "province": "Flores Timur, Nusa Tenggara Timur",
        "elevation_m": 1702, "level": 2, "level_name": "Level II (Waspada)", "color": "#eab308",
        "radius_bahaya_km": 2.0, "last_vona": "Emisi asap kawah putih", "coords": [122.787, -8.553], "region": "Bali & Nusa Tenggara"
    },
    {
        "id": "iliboleng", "name": "G. Iliboleng", "province": "Adonara, Flores Timur, Nusa Tenggara Timur",
        "elevation_m": 1659, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.0, "last_vona": "Aktivitas kawah normal", "coords": [123.257, -8.342], "region": "Bali & Nusa Tenggara"
    },
    {
        "id": "lewotolo", "name": "G. Lewotolo", "province": "Lembata, Nusa Tenggara Timur",
        "elevation_m": 1423, "level": 3, "level_name": "Level III (Siaga)", "color": "#f97316",
        "radius_bahaya_km": 3.0, "last_vona": "Letusan eksplosif strombolian menerus", "coords": [123.505, -8.272], "region": "Bali & Nusa Tenggara"
    },
    {
        "id": "ile_werung", "name": "G. Ile Werung", "province": "Lembata, Nusa Tenggara Timur",
        "elevation_m": 1018, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.0, "last_vona": "Aktivitas normal", "coords": [123.570, -8.530], "region": "Bali & Nusa Tenggara"
    },
    {
        "id": "batu_tara", "name": "G. Batu Tara", "province": "P. Komba, Lembata, Nusa Tenggara Timur",
        "elevation_m": 748, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Letusan freatik laut normal", "coords": [123.579, -7.792], "region": "Bali & Nusa Tenggara"
    },
    {
        "id": "sirung", "name": "G. Sirung", "province": "P. Pantar, Alor, Nusa Tenggara Timur",
        "elevation_m": 862, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Aktivitas kawah normal", "coords": [124.130, -8.508], "region": "Bali & Nusa Tenggara"
    },

    # --- SULAWESI & SANGIHE (10) ---
    {
        "id": "colo", "name": "G. Colo (Una-una)", "province": "Teluk Tomini, Tojo Una-Una, Sulteng",
        "elevation_m": 507, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Aktivitas normal", "coords": [121.610, -0.170], "region": "Sulawesi"
    },
    {
        "id": "ambang", "name": "G. Ambang", "province": "Bolaang Mongondow Timur, Sulut",
        "elevation_m": 1795, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Aktivitas solfatara normal", "coords": [124.420, 0.750], "region": "Sulawesi"
    },
    {
        "id": "soputan", "name": "G. Soputan", "province": "Minahasa Tenggara, Sulawesi Utara",
        "elevation_m": 1785, "level": 2, "level_name": "Level II (Waspada)", "color": "#eab308",
        "radius_bahaya_km": 2.0, "last_vona": "Emisi asap kawah putih tipis", "coords": [124.737, 1.112], "region": "Sulawesi"
    },
    {
        "id": "lokon", "name": "G. Lokon", "province": "Tomohon, Sulawesi Utara",
        "elevation_m": 1580, "level": 2, "level_name": "Level II (Waspada)", "color": "#eab308",
        "radius_bahaya_km": 1.5, "last_vona": "Peningkatan kegempaan vulkanik Tompaluan", "coords": [124.793, 1.358], "region": "Sulawesi"
    },
    {
        "id": "mahawu", "name": "G. Mahawu", "province": "Tomohon, Sulawesi Utara",
        "elevation_m": 1324, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.0, "last_vona": "Danau kawah normal", "coords": [124.860, 1.358], "region": "Sulawesi"
    },
    {
        "id": "klabat", "name": "G. Klabat", "province": "Minahasa Utara, Sulawesi Utara",
        "elevation_m": 1995, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.0, "last_vona": "Aktivitas normal", "coords": [125.030, 1.470], "region": "Sulawesi"
    },
    {
        "id": "tangkoko", "name": "G. Tangkoko", "province": "Bitung, Sulawesi Utara",
        "elevation_m": 1149, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.0, "last_vona": "Aktivitas kawah normal", "coords": [125.200, 1.520], "region": "Sulawesi"
    },
    {
        "id": "ruang", "name": "G. Ruang", "province": "Kep. Sitaro, Sulawesi Utara",
        "elevation_m": 725, "level": 3, "level_name": "Level III (Siaga)", "color": "#f97316",
        "radius_bahaya_km": 4.0, "last_vona": "Erupsi eksplosif paroksimal", "coords": [125.370, 2.303], "region": "Sulawesi"
    },
    {
        "id": "karangetang", "name": "G. Karangetang", "province": "Kep. Sitaro, Sulawesi Utara",
        "elevation_m": 1784, "level": 3, "level_name": "Level III (Siaga)", "color": "#f97316",
        "radius_bahaya_km": 3.5, "last_vona": "Leleran lava pijar aktif Kawah Utama", "coords": [125.405, 2.781], "region": "Sulawesi"
    },
    {
        "id": "awu", "name": "G. Awu", "province": "Kep. Sangihe, Sulawesi Utara",
        "elevation_m": 1320, "level": 3, "level_name": "Level III (Siaga)", "color": "#f97316",
        "radius_bahaya_km": 5.0, "last_vona": "Peningkatan gempa vulkanik dangkal", "coords": [125.450, 3.670], "region": "Sulawesi"
    },

    # --- MALUKU & MALUKU UTARA (10) ---
    {
        "id": "gamalama", "name": "G. Gamalama", "province": "Ternate, Maluku Utara",
        "elevation_m": 1715, "level": 2, "level_name": "Level II (Waspada)", "color": "#eab308",
        "radius_bahaya_km": 1.5, "last_vona": "Emisi asap kawah putih kelabu", "coords": [127.330, 0.800], "region": "Maluku & Papua"
    },
    {
        "id": "tidore", "name": "G. Tidore (Kie Matubu)", "province": "Tidore, Maluku Utara",
        "elevation_m": 1730, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.0, "last_vona": "Aktivitas kawah normal", "coords": [127.400, 0.660], "region": "Maluku & Papua"
    },
    {
        "id": "gamkonora", "name": "G. Gamkonora", "province": "Halmahera Barat, Maluku Utara",
        "elevation_m": 1635, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Aktivitas kawah normal", "coords": [127.530, 1.380], "region": "Maluku & Papua"
    },
    {
        "id": "ibu", "name": "G. Ibu", "province": "Halmahera Barat, Maluku Utara",
        "elevation_m": 1325, "level": 3, "level_name": "Level III (Siaga)", "color": "#f97316",
        "radius_bahaya_km": 5.0, "last_vona": "Erupsi abu vertikal 4.000m", "coords": [127.630, 1.488], "region": "Maluku & Papua"
    },
    {
        "id": "dukono", "name": "G. Dukono", "province": "Halmahera Utara, Maluku Utara",
        "elevation_m": 1229, "level": 2, "level_name": "Level II (Waspada)", "color": "#eab308",
        "radius_bahaya_km": 3.0, "last_vona": "Letusan menerus abu vulkanik Malupang", "coords": [127.894, 1.693], "region": "Maluku & Papua"
    },
    {
        "id": "kie_besi", "name": "G. Kie Besi (Makian)", "province": "Halmahera Selatan, Maluku Utara",
        "elevation_m": 1357, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Aktivitas normal", "coords": [127.400, 0.320], "region": "Maluku & Papua"
    },
    {
        "id": "banda_api", "name": "G. Banda Api", "province": "Kep. Banda, Maluku Tengah",
        "elevation_m": 640, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.0, "last_vona": "Aktivitas solfatara normal", "coords": [129.871, -4.525], "region": "Maluku & Papua"
    },
    {
        "id": "nila", "name": "G. Nila", "province": "Maluku Barat Daya",
        "elevation_m": 781, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Aktivitas pulau gunungapi normal", "coords": [129.500, -6.730], "region": "Maluku & Papua"
    },
    {
        "id": "serua", "name": "G. Serua", "province": "Maluku Tengah",
        "elevation_m": 641, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Aktivitas normal", "coords": [130.000, -6.300], "region": "Maluku & Papua"
    },
    {
        "id": "teon", "name": "G. Teon", "province": "Maluku Barat Daya",
        "elevation_m": 655, "level": 1, "level_name": "Level I (Normal)", "color": "#22c55e",
        "radius_bahaya_km": 1.5, "last_vona": "Aktivitas normal", "coords": [129.120, -6.920], "region": "Maluku & Papua"
    }
]

def build_geojson():
    features = []
    for v in ALL_VOLCANOES:
        features.append({
            "type": "Feature",
            "properties": {
                "id": v["id"],
                "name": v["name"],
                "province": v["province"],
                "region": v["region"],
                "elevation_m": v["elevation_m"],
                "level": v["level"],
                "level_name": v["level_name"],
                "color": v["color"],
                "radius_bahaya_km": v["radius_bahaya_km"],
                "last_vona": v["last_vona"],
                "has_event": True,
                "event_id": v["id"]
            },
            "geometry": {
                "type": "Point",
                "coordinates": v["coords"]
            }
        })

    geo = {
        "type": "FeatureCollection",
        "name": "volcanoes_indonesia_pvmbg_national",
        "metadata": {
            "source": "Pusat Vulkanologi dan Mitigasi Bencana Geologi (PVMBG) - Badan Geologi ESDM RI",
            "total_volcanoes": len(features),
            "coverage": "Seluruh Wilayah Republik Indonesia (Sumatera, Jawa, Bali, NTB, NTT, Maluku, Sulawesi)"
        },
        "features": features
    }
    return geo

if __name__ == "__main__":
    out_path = Path(__file__).resolve().parents[2] / "data" / "layers" / "volcanoes_indonesia.geojson"
    geo_data = build_geojson()
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(geo_data, f, indent=2, ensure_ascii=False)
    print(f"Berhasil menghasilkan {len(geo_data['features'])} gunung api nasional ke {out_path}")
