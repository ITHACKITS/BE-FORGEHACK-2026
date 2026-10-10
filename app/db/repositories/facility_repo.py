"""
app/db/repositories/facility_repo.py

Public facility access backed by the SQLite R*Tree index.
Reads only return the types in PUBLIC_FACILITY_TYPES (airports); other rows stay stored.
"""

import json
from typing import Any, Dict, List, Optional

from app.core.config import PUBLIC_FACILITY_TYPES
from app.db.session import get_db, get_db_connection

_TYPE_PLACEHOLDERS = ", ".join("?" for _ in PUBLIC_FACILITY_TYPES)


def _is_public(facility_type: Optional[str]) -> bool:
    return facility_type is None or facility_type in PUBLIC_FACILITY_TYPES


class FacilityRepository:
    @staticmethod
    def get_by_bbox(
        lat_min: float,
        lat_max: float,
        lon_min: float,
        lon_max: float,
        facility_type: Optional[str] = None,
        limit: Optional[int] = 200,
        zoom: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Kueri fasilitas di dalam batas kotak (Bounding Box) menggunakan indeks R*Tree.
        Mendukung Level-of-Detail (LOD) cerdas jika parameter zoom disertakan.
        """
        if not _is_public(facility_type):
            return []
        conn = get_db_connection()
        try:
            # R*Tree join: minX/maxX are longitude, minY/maxY are latitude
            params: List[Any] = [lon_min, lon_max, lat_min, lat_max, *PUBLIC_FACILITY_TYPES]
            where_clauses = [
                "idx.minX >= ? AND idx.maxX <= ?",
                "idx.minY >= ? AND idx.maxY <= ?",
                f"f.facility_type IN ({_TYPE_PLACEHOLDERS})",
            ]

            if facility_type:
                where_clauses.append("f.facility_type = ?")
                params.append(facility_type)

            sql = f"""
                SELECT f.facility_id, f.name, f.facility_type, f.latitude, f.longitude, f.district, f.province, f.metadata_json
                FROM facilities f
                JOIN facilities_rtree idx ON f.rowid = idx.id
                WHERE {" AND ".join(where_clauses)}
            """

            if limit is not None and limit > 0:
                sql += " LIMIT ?"
                params.append(limit)

            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()

            results = []
            for row in rows:
                meta = json.loads(row["metadata_json"]) if row["metadata_json"] else {}
                item = {
                    "facility_id": row["facility_id"],
                    "name": row["name"],
                    "facility_type": row["facility_type"],
                    "latitude": row["latitude"],
                    "longitude": row["longitude"],
                    "district": row["district"] or "-",
                    "province": row["province"] or "-",
                    **meta
                }
                results.append(item)
            return results
        finally:
            conn.close()

    @staticmethod
    def get_by_id(facility_id: str) -> Optional[Dict[str, Any]]:
        """Mencari fasilitas tunggal berdasarkan ID unik."""
        conn = get_db_connection()
        try:
            cursor = conn.execute(
                "SELECT facility_id, name, facility_type, latitude, longitude, district, province, metadata_json "
                f"FROM facilities WHERE facility_id = ? AND facility_type IN ({_TYPE_PLACEHOLDERS})",
                (facility_id, *PUBLIC_FACILITY_TYPES)
            )
            row = cursor.fetchone()
            if not row:
                return None
            meta = json.loads(row["metadata_json"]) if row["metadata_json"] else {}
            return {
                "facility_id": row["facility_id"],
                "name": row["name"],
                "facility_type": row["facility_type"],
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "district": row["district"] or "-",
                "province": row["province"] or "-",
                **meta
            }
        finally:
            conn.close()

    @staticmethod
    def get_all(
        facility_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """All public facilities, optionally filtered by type."""
        if not _is_public(facility_type):
            return []
        conn = get_db_connection()
        try:
            sql = (
                "SELECT facility_id, name, facility_type, latitude, longitude, district, province, metadata_json "
                f"FROM facilities WHERE facility_type IN ({_TYPE_PLACEHOLDERS})"
            )
            params: List[Any] = list(PUBLIC_FACILITY_TYPES)
            if facility_type:
                sql += " AND facility_type = ?"
                params.append(facility_type)
            if limit:
                sql += " LIMIT ?"
                params.append(limit)

            cursor = conn.execute(sql, params)
            results = []
            for row in cursor.fetchall():
                meta = json.loads(row["metadata_json"]) if row["metadata_json"] else {}
                results.append({
                    "facility_id": row["facility_id"],
                    "name": row["name"],
                    "facility_type": row["facility_type"],
                    "latitude": row["latitude"],
                    "longitude": row["longitude"],
                    "district": row["district"] or "-",
                    "province": row["province"] or "-",
                    **meta
                })
            return results
        finally:
            conn.close()

    @staticmethod
    def count_all(facility_type: Optional[str] = None) -> int:
        """Number of public facilities."""
        if not _is_public(facility_type):
            return 0
        conn = get_db_connection()
        try:
            sql = f"SELECT COUNT(*) FROM facilities WHERE facility_type IN ({_TYPE_PLACEHOLDERS})"
            params: List[Any] = list(PUBLIC_FACILITY_TYPES)
            if facility_type:
                sql += " AND facility_type = ?"
                params.append(facility_type)
            cursor = conn.execute(sql, params)
            return cursor.fetchone()[0]
        finally:
            conn.close()

    @staticmethod
    def upsert_batch(facilities: List[Dict[str, Any]]) -> int:
        """
        Menyimpan atau memperbarui data fasilitas secara atomik dalam satu transaksi.
        Triggers R*Tree otomatis menjaga konsistensi indeks spasial.
        """
        if not facilities:
            return 0

        with get_db() as conn:
            stmt = """
                INSERT INTO facilities (facility_id, name, facility_type, latitude, longitude, district, province, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(facility_id) DO UPDATE SET
                    name = excluded.name,
                    facility_type = excluded.facility_type,
                    latitude = excluded.latitude,
                    longitude = excluded.longitude,
                    district = excluded.district,
                    province = excluded.province,
                    metadata_json = excluded.metadata_json
            """
            rows_to_insert = []
            for f in facilities:
                # Pisahkan atribut dasar dan sisa metadata
                fid = f.get("facility_id") or f.get("id")
                name = f.get("name", "Tanpa Nama")
                ftype = f.get("facility_type", "school")
                lat = float(f.get("latitude") or f.get("lat") or 0.0)
                lon = float(f.get("longitude") or f.get("lon") or 0.0)
                district = f.get("district")
                province = f.get("province")

                excluded_keys = {"facility_id", "id", "name", "facility_type", "latitude", "lat", "longitude", "lon", "district", "province"}
                meta = {k: v for k, v in f.items() if k not in excluded_keys}
                meta_json = json.dumps(meta, ensure_ascii=False) if meta else None

                rows_to_insert.append((fid, name, ftype, lat, lon, district, province, meta_json))

            conn.executemany(stmt, rows_to_insert)
            return len(rows_to_insert)
