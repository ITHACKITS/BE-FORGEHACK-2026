"""
app/db/repositories/volcano_repo.py

Repository akses data 70 gunung api aktif PVMBG se-Indonesia
dengan integrasi indeks spasial R*Tree dan format GeoJSON standar.
"""

import json
from typing import Any, Dict, List, Optional

from app.db.session import get_db, get_db_connection


class VolcanoRepository:
    @staticmethod
    def get_all(
        lat_min: Optional[float] = None,
        lat_max: Optional[float] = None,
        lon_min: Optional[float] = None,
        lon_max: Optional[float] = None,
        level_min: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Mengambil daftar gunung api. Jika koordinat batas (BBOX) disediakan,
        kueri dieksekusi secara instan menggunakan indeks spasial volcanoes_rtree.
        """
        conn = get_db_connection()
        try:
            if None not in (lat_min, lat_max, lon_min, lon_max):
                params: List[Any] = [lon_min, lon_max, lat_min, lat_max]
                where = ["idx.minX >= ? AND idx.maxX <= ?", "idx.minY >= ? AND idx.maxY <= ?"]
                if level_min is not None:
                    where.append("v.level >= ?")
                    params.append(level_min)

                sql = f"""
                    SELECT v.* FROM volcanoes v
                    JOIN volcanoes_rtree idx ON v.rowid = idx.id
                    WHERE {" AND ".join(where)}
                    ORDER BY v.level DESC, v.name ASC
                """
                cursor = conn.execute(sql, params)
            else:
                params = []
                sql = "SELECT * FROM volcanoes"
                if level_min is not None:
                    sql += " WHERE level >= ?"
                    params.append(level_min)
                sql += " ORDER BY level DESC, name ASC"
                cursor = conn.execute(sql, params)

            results = []
            for row in cursor.fetchall():
                meta = json.loads(row["metadata_json"]) if row["metadata_json"] else {}
                item = {
                    "id": row["id"],
                    "name": row["name"],
                    "province": row["province"],
                    "region": row["region"],
                    "elevation_m": row["elevation_m"],
                    "level": row["level"],
                    "level_name": row["level_name"],
                    "color": row["color"],
                    "radius_bahaya_km": row["radius_bahaya_km"],
                    "last_vona": row["last_vona"],
                    "latitude": row["latitude"],
                    "longitude": row["longitude"],
                    "has_event": bool(row["has_event"]),
                    "event_id": row["event_id"],
                    **meta
                }
                results.append(item)
            return results
        finally:
            conn.close()

    @staticmethod
    def get_by_id(volcano_id: str) -> Optional[Dict[str, Any]]:
        """Mengambil data gunung api spesifik berdasarkan ID."""
        conn = get_db_connection()
        try:
            cursor = conn.execute("SELECT * FROM volcanoes WHERE id = ?", (volcano_id,))
            row = cursor.fetchone()
            if not row:
                return None
            meta = json.loads(row["metadata_json"]) if row["metadata_json"] else {}
            return {
                "id": row["id"],
                "name": row["name"],
                "province": row["province"],
                "region": row["region"],
                "elevation_m": row["elevation_m"],
                "level": row["level"],
                "level_name": row["level_name"],
                "color": row["color"],
                "radius_bahaya_km": row["radius_bahaya_km"],
                "last_vona": row["last_vona"],
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "has_event": bool(row["has_event"]),
                "event_id": row["event_id"],
                **meta
            }
        finally:
            conn.close()

    @staticmethod
    def to_geojson_collection(volcanoes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Konversi list objek gunung api ke GeoJSON FeatureCollection standar RFC 7946."""
        features = []
        for v in volcanoes:
            features.append({
                "type": "Feature",
                "properties": {
                    "id": v["id"],
                    "name": v["name"],
                    "province": v.get("province", "-"),
                    "region": v.get("region", "-"),
                    "elevation_m": v.get("elevation_m", 0),
                    "level": v.get("level", 1),
                    "level_name": v.get("level_name", "Level I (Normal)"),
                    "color": v.get("color", "#22c55e"),
                    "radius_bahaya_km": v.get("radius_bahaya_km", 3.0),
                    "last_vona": v.get("last_vona", "Aktivitas Normal"),
                    "has_event": v.get("has_event", False),
                    "event_id": v.get("event_id")
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [v["longitude"], v["latitude"]]
                }
            })
        return {
            "type": "FeatureCollection",
            "metadata": {
                "source": "Pusat Vulkanologi dan Mitigasi Bencana Geologi (PVMBG) - Badan Geologi Kementerian ESDM RI",
                "total_volcanoes": len(features)
            },
            "features": features
        }

    @staticmethod
    def count_all() -> int:
        """Menghitung total gunung api di database."""
        conn = get_db_connection()
        try:
            return conn.execute("SELECT COUNT(*) FROM volcanoes").fetchone()[0]
        finally:
            conn.close()

    @staticmethod
    def upsert_batch(volcanoes: List[Dict[str, Any]]) -> int:
        """Batch upsert seluruh katalog gunung api nasional."""
        if not volcanoes:
            return 0

        with get_db() as conn:
            stmt = """
                INSERT INTO volcanoes (
                    id, name, province, region, elevation_m, level, level_name,
                    color, radius_bahaya_km, last_vona, latitude, longitude,
                    has_event, event_id, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    province = excluded.province,
                    region = excluded.region,
                    elevation_m = excluded.elevation_m,
                    level = excluded.level,
                    level_name = excluded.level_name,
                    color = excluded.color,
                    radius_bahaya_km = excluded.radius_bahaya_km,
                    last_vona = excluded.last_vona,
                    latitude = excluded.latitude,
                    longitude = excluded.longitude,
                    has_event = excluded.has_event,
                    event_id = excluded.event_id,
                    metadata_json = excluded.metadata_json
            """
            rows = []
            for v in volcanoes:
                vid = v.get("id")
                name = v.get("name")
                prov = v.get("province")
                reg = v.get("region")
                elev = float(v.get("elevation_m", 0.0))
                lvl = int(v.get("level", 1))
                lvl_name = v.get("level_name", "Level I (Normal)")
                color = v.get("color", "#22c55e")
                radius = float(v.get("radius_bahaya_km", 3.0))
                vona = v.get("last_vona", "Aktivitas Normal")
                lat = float(v.get("latitude") if "latitude" in v else v.get("lat", 0.0))
                lon = float(v.get("longitude") if "longitude" in v else v.get("lon", 0.0))
                has_evt = bool(v.get("has_event", False))
                evt_id = v.get("event_id")

                keys = {"id", "name", "province", "region", "elevation_m", "level", "level_name", "color", "radius_bahaya_km", "last_vona", "latitude", "longitude", "lat", "lon", "has_event", "event_id"}
                meta = {k: val for k, val in v.items() if k not in keys}
                meta_json = json.dumps(meta, ensure_ascii=False) if meta else None

                rows.append((vid, name, prov, reg, elev, lvl, lvl_name, color, radius, vona, lat, lon, has_evt, evt_id, meta_json))

            conn.executemany(stmt, rows)
            return len(rows)
