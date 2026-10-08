"""
app/db/repositories/forest_repo.py

Repository akses data 36 kawasan hutan & lahan gambut kritis
termasuk penyimpanan poligon batas spasial riil untuk evaluasi Point-in-Polygon.
"""

import json
from typing import Any, Dict, List, Optional

from app.db.session import get_db, get_db_connection


class ForestRepository:
    @staticmethod
    def get_all(
        lat_min: Optional[float] = None,
        lat_max: Optional[float] = None,
        lon_min: Optional[float] = None,
        lon_max: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Mengambil seluruh kawasan hutan atau menyaring dengan kotak spasial R*Tree."""
        conn = get_db_connection()
        try:
            if None not in (lat_min, lat_max, lon_min, lon_max):
                sql = """
                    SELECT f.id, f.name, f.forest_type, f.province, f.region,
                           f.latitude, f.longitude, f.area_ha, f.risk_level,
                           f.n_hotspots, f.description
                    FROM forests f
                    JOIN forests_rtree idx ON f.rowid = idx.id
                    WHERE idx.minX >= ? AND idx.maxX <= ?
                      AND idx.minY >= ? AND idx.maxY <= ?
                    ORDER BY f.n_hotspots DESC
                """
                cursor = conn.execute(sql, (lon_min, lon_max, lat_min, lat_max))
            else:
                sql = """
                    SELECT id, name, forest_type, province, region,
                           latitude, longitude, area_ha, risk_level,
                           n_hotspots, description
                    FROM forests
                    ORDER BY n_hotspots DESC
                """
                cursor = conn.execute(sql)

            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row["id"],
                    "name": row["name"],
                    "forest_type": row["forest_type"],
                    "province": row["province"],
                    "region": row["region"],
                    "lat": row["latitude"],
                    "lon": row["longitude"],
                    "area_ha": row["area_ha"],
                    "risk_level": row["risk_level"],
                    "risk": row["risk_level"],
                    "n_hotspots": row["n_hotspots"],
                    "description": row["description"]
                })
            return results
        finally:
            conn.close()

    @staticmethod
    def get_by_id(forest_id: str) -> Optional[Dict[str, Any]]:
        """Mengambil satu kawasan hutan beserta geometri batas poligonnya."""
        conn = get_db_connection()
        try:
            cursor = conn.execute("SELECT * FROM forests WHERE id = ?", (forest_id,))
            row = cursor.fetchone()
            if not row:
                return None
            geom = json.loads(row["geometry_geojson"]) if row["geometry_geojson"] else None
            return {
                "id": row["id"],
                "name": row["name"],
                "forest_type": row["forest_type"],
                "province": row["province"],
                "region": row["region"],
                "lat": row["latitude"],
                "lon": row["longitude"],
                "area_ha": row["area_ha"],
                "risk_level": row["risk_level"],
                "n_hotspots": row["n_hotspots"],
                "description": row["description"],
                "geometry": geom
            }
        finally:
            conn.close()

    @staticmethod
    def get_all_boundaries_geojson() -> Dict[str, Any]:
        """Mengambil seluruh batas poligon kawasan hutan dalam format FeatureCollection."""
        conn = get_db_connection()
        try:
            cursor = conn.execute(
                "SELECT id, name, forest_type, province, area_ha, risk_level, n_hotspots, geometry_geojson "
                "FROM forests WHERE geometry_geojson IS NOT NULL"
            )
            features = []
            for row in cursor.fetchall():
                geom = json.loads(row["geometry_geojson"])
                features.append({
                    "type": "Feature",
                    "id": row["id"],
                    "properties": {
                        "id": row["id"],
                        "forest_id": row["id"],
                        "name": row["name"],
                        "forest_type": row["forest_type"],
                        "province": row["province"],
                        "area_ha": row["area_ha"],
                        "risk_level": row["risk_level"],
                        "n_hotspots": row["n_hotspots"]
                    },
                    "geometry": geom
                })
            return {
                "type": "FeatureCollection",
                "metadata": {
                    "source": "Kementerian Lingkungan Hidup dan Kehutanan (KLHK) & BRGM",
                    "total_features": len(features)
                },
                "features": features
            }
        finally:
            conn.close()

    @staticmethod
    def upsert_batch(forests: List[Dict[str, Any]]) -> int:
        """Batch upsert seluruh kawasan hutan beserta geometri poligon spasialnya."""
        if not forests:
            return 0

        with get_db() as conn:
            stmt = """
                INSERT INTO forests (
                    id, name, forest_type, province, region,
                    latitude, longitude, area_ha, risk_level,
                    n_hotspots, description, geometry_geojson
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    forest_type = excluded.forest_type,
                    province = excluded.province,
                    region = excluded.region,
                    latitude = excluded.latitude,
                    longitude = excluded.longitude,
                    area_ha = excluded.area_ha,
                    risk_level = excluded.risk_level,
                    n_hotspots = excluded.n_hotspots,
                    description = excluded.description,
                    geometry_geojson = COALESCE(excluded.geometry_geojson, forests.geometry_geojson)
            """
            rows = []
            for f in forests:
                fid = f.get("id") or f.get("forest_id")
                name = f.get("name")
                ftype = f.get("forest_type")
                prov = f.get("province")
                reg = f.get("region")
                lat = float(f.get("latitude") if "latitude" in f else f.get("lat", 0.0))
                lon = float(f.get("longitude") if "longitude" in f else f.get("lon", 0.0))
                area = float(f.get("area_ha", 0.0))
                risk = f.get("risk_level", "Rawan")
                n_hot = int(f.get("n_hotspots", 0))
                desc = f.get("description", "")
                geom = f.get("geometry") or f.get("geometry_geojson")
                geom_json = json.dumps(geom, ensure_ascii=False) if isinstance(geom, dict) else geom

                rows.append((fid, name, ftype, prov, reg, lat, lon, area, risk, n_hot, desc, geom_json))

            conn.executemany(stmt, rows)
            return len(rows)
