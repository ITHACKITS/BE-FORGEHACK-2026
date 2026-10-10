"""
app/db/schema.py

Definisi skema DDL terpusat dan pemicu (triggers) indeks spasial R*Tree
untuk sistem informasi geografis UdaraSiaga.
"""

import sqlite3

DDL_SCHEMA = """
-- ============================================================================
-- 1. TABEL GUNUNG BERAPI (VOLCANOES)
-- ============================================================================
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

CREATE INDEX IF NOT EXISTS idx_volcanoes_level ON volcanoes(level);
CREATE INDEX IF NOT EXISTS idx_volcanoes_region ON volcanoes(region);

-- Indeks Spasial R*Tree untuk Gunung Api
CREATE VIRTUAL TABLE IF NOT EXISTS volcanoes_rtree USING rtree(
    id,          -- Mereferensikan volcanoes.rowid
    minX, maxX,  -- Lintang Bujur (longitude)
    minY, maxY   -- Bujur Lintang (latitude)
);

-- ============================================================================
-- 2. TABEL KAWASAN HUTAN & LAHAN GAMBUT (FORESTS)
-- ============================================================================
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
    geometry_geojson TEXT -- Poligon batas spasial riil dalam format GeoJSON string
);

CREATE INDEX IF NOT EXISTS idx_forests_province ON forests(province);
CREATE INDEX IF NOT EXISTS idx_forests_region ON forests(region);

-- Indeks Spasial R*Tree untuk Titik Centroid Hutan
CREATE VIRTUAL TABLE IF NOT EXISTS forests_rtree USING rtree(
    id,
    minX, maxX,
    minY, maxY
);

-- ============================================================================
-- 3. TABEL FASILITAS PUBLIK (FACILITIES: SEKOLAH, FASKES, BANDARA)
-- ============================================================================
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

CREATE INDEX IF NOT EXISTS idx_facilities_type ON facilities(facility_type);
CREATE INDEX IF NOT EXISTS idx_facilities_district ON facilities(district);
CREATE INDEX IF NOT EXISTS idx_facilities_province ON facilities(province);

-- Indeks Spasial R*Tree untuk Fasilitas (Mendukung ratusan ribu titik tanpa lemot)
CREATE VIRTUAL TABLE IF NOT EXISTS facilities_rtree USING rtree(
    id,          -- facilities.rowid
    minX, maxX,  -- longitude
    minY, maxY   -- latitude
);

-- ============================================================================
-- 4. TABEL TITIK API / HOTSPOTS (FIRMS)
-- ============================================================================
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

CREATE INDEX IF NOT EXISTS idx_hotspots_event ON hotspots(event_id);
CREATE INDEX IF NOT EXISTS idx_hotspots_date ON hotspots(acq_date);

CREATE VIRTUAL TABLE IF NOT EXISTS hotspots_rtree USING rtree(
    id,          -- hotspots.rowid
    minX, maxX,
    minY, maxY
);

-- ============================================================================
-- 5. TABEL KATALOG EVENT & SIMULATION RUNS
-- ============================================================================
CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    hazard_type TEXT NOT NULL, -- 'volcano' atau 'forest_fire'
    target_id TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    metadata_json TEXT
);

CREATE TABLE IF NOT EXISTS simulation_runs (
    run_id TEXT PRIMARY KEY,
    event_id TEXT,
    hazard_type TEXT NOT NULL,
    created_at TEXT NOT NULL,
    scenario_label TEXT,
    status TEXT,
    results_json TEXT
);
"""


TRIGGERS_SCHEMA = """
-- ============================================================================
-- TRIGGERS UNTUK MENJAGA SINKRONISASI OTOMATIS ANTARA TABEL UTAMA & R*TREE
-- ============================================================================

-- 1. Triggers Facilities
DROP TRIGGER IF EXISTS trg_facilities_insert;
CREATE TRIGGER trg_facilities_insert AFTER INSERT ON facilities BEGIN
    INSERT INTO facilities_rtree(id, minX, maxX, minY, maxY)
    VALUES (new.rowid, new.longitude, new.longitude, new.latitude, new.latitude);
END;

DROP TRIGGER IF EXISTS trg_facilities_delete;
CREATE TRIGGER trg_facilities_delete AFTER DELETE ON facilities BEGIN
    DELETE FROM facilities_rtree WHERE id = old.rowid;
END;

DROP TRIGGER IF EXISTS trg_facilities_update;
CREATE TRIGGER trg_facilities_update AFTER UPDATE ON facilities BEGIN
    DELETE FROM facilities_rtree WHERE id = old.rowid;
    INSERT INTO facilities_rtree(id, minX, maxX, minY, maxY)
    VALUES (new.rowid, new.longitude, new.longitude, new.latitude, new.latitude);
END;

-- 2. Triggers Volcanoes
DROP TRIGGER IF EXISTS trg_volcanoes_insert;
CREATE TRIGGER trg_volcanoes_insert AFTER INSERT ON volcanoes BEGIN
    INSERT INTO volcanoes_rtree(id, minX, maxX, minY, maxY)
    VALUES (new.rowid, new.longitude, new.longitude, new.latitude, new.latitude);
END;

DROP TRIGGER IF EXISTS trg_volcanoes_delete;
CREATE TRIGGER trg_volcanoes_delete AFTER DELETE ON volcanoes BEGIN
    DELETE FROM volcanoes_rtree WHERE id = old.rowid;
END;

DROP TRIGGER IF EXISTS trg_volcanoes_update;
CREATE TRIGGER trg_volcanoes_update AFTER UPDATE ON volcanoes BEGIN
    DELETE FROM volcanoes_rtree WHERE id = old.rowid;
    INSERT INTO volcanoes_rtree(id, minX, maxX, minY, maxY)
    VALUES (new.rowid, new.longitude, new.longitude, new.latitude, new.latitude);
END;

-- 3. Triggers Forests
DROP TRIGGER IF EXISTS trg_forests_insert;
CREATE TRIGGER trg_forests_insert AFTER INSERT ON forests BEGIN
    INSERT INTO forests_rtree(id, minX, maxX, minY, maxY)
    VALUES (new.rowid, new.longitude, new.longitude, new.latitude, new.latitude);
END;

DROP TRIGGER IF EXISTS trg_forests_delete;
CREATE TRIGGER trg_forests_delete AFTER DELETE ON forests BEGIN
    DELETE FROM forests_rtree WHERE id = old.rowid;
END;

DROP TRIGGER IF EXISTS trg_forests_update;
CREATE TRIGGER trg_forests_update AFTER UPDATE ON forests BEGIN
    DELETE FROM forests_rtree WHERE id = old.rowid;
    INSERT INTO forests_rtree(id, minX, maxX, minY, maxY)
    VALUES (new.rowid, new.longitude, new.longitude, new.latitude, new.latitude);
END;

-- 4. Triggers Hotspots
DROP TRIGGER IF EXISTS trg_hotspots_insert;
CREATE TRIGGER trg_hotspots_insert AFTER INSERT ON hotspots BEGIN
    INSERT INTO hotspots_rtree(id, minX, maxX, minY, maxY)
    VALUES (new.rowid, new.longitude, new.longitude, new.latitude, new.latitude);
END;

DROP TRIGGER IF EXISTS trg_hotspots_delete;
CREATE TRIGGER trg_hotspots_delete AFTER DELETE ON hotspots BEGIN
    DELETE FROM hotspots_rtree WHERE id = old.rowid;
END;
"""


def init_db_schema(conn: sqlite3.Connection) -> None:
    """
    Menginisialisasi seluruh tabel, indeks B-Tree, R*Tree, dan triggers.
    """
    cursor = conn.cursor()
    cursor.executescript(DDL_SCHEMA)
    cursor.executescript(TRIGGERS_SCHEMA)
    conn.commit()
