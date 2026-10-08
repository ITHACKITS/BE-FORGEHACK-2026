"""
app/db/repositories/facility_repo.py

Repository akses data fasilitas publik (sekolah, faskes, bandara)
memanfaatkan indeks spasial R*Tree SQLite untuk kueri BBOX sub-milidetik.
"""

import json
from typing import Any, Dict, List, Optional

from app.db.session import get_db, get_db_connection


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
        conn = get_db_connection()
        try:
            # Bangun kueri berbasis R*Tree join tabel facilities
            # minX/maxX adalah longitude, minY/maxY adalah latitude
            params: List[Any] = [lon_min, lon_max, lat_min, lat_max]
            where_clauses = [
                "idx.minX >= ? AND idx.maxX <= ?",
                "idx.minY >= ? AND idx.maxY <= ?"
            ]

            if facility_type:
                where_clauses.append("f.facility_type = ?")
                params.append(facility_type)
            elif zoom is not None:
                # Hierarchical LOD: di zoom jauh jangan tampilkan sekolah kecil agar peta bersih
                if zoom < 8:
                    where_clauses.append("f.facility_type IN ('airport', 'healthcare')")
                elif zoom < 10:
                    where_clauses.append("(f.facility_type IN ('airport', 'healthcare') OR f.name LIKE '%SMA%' OR f.name LIKE '%SMK%')")

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
                "FROM facilities WHERE facility_id = ?",
                (facility_id,)
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
        """Mengambil seluruh fasilitas dengan filter opsional."""
        conn = get_db_connection()
        try:
            sql = "SELECT facility_id, name, facility_type, latitude, longitude, district, province, metadata_json FROM facilities"
            params: List[Any] = []
            if facility_type:
                sql += " WHERE facility_type = ?"
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
        """Menghitung total fasilitas di database."""
        conn = get_db_connection()
        try:
            if facility_type:
                cursor = conn.execute("SELECT COUNT(*) FROM facilities WHERE facility_type = ?", (facility_type,))
            else:
                cursor = conn.execute("SELECT COUNT(*) FROM facilities")
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
