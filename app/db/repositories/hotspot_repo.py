"""
app/db/repositories/hotspot_repo.py

Repository akses data titik api satelit NASA FIRMS (VIIRS & MODIS)
dengan pengindeksan spasial R*Tree dan filter berbasis event / bbox.
"""

from typing import Any, Dict, List, Optional

from app.db.session import get_db, get_db_connection


class HotspotRepository:
    @staticmethod
    def get_by_event(
        event_id: str = "national",
        lat_min: Optional[float] = None,
        lat_max: Optional[float] = None,
        lon_min: Optional[float] = None,
        lon_max: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Mengambil titik api untuk event tertentu atau skala nasional."""
        conn = get_db_connection()
        try:
            params: List[Any] = []
            where = []

            # Jika bukan national/all, saring event_id
            if event_id not in ["national", "all", "indonesia"]:
                where.append("h.event_id = ?")
                params.append(event_id)

            if None not in (lat_min, lat_max, lon_min, lon_max):
                params.extend([lon_min, lon_max, lat_min, lat_max])
                where.extend([
                    "idx.minX >= ? AND idx.maxX <= ?",
                    "idx.minY >= ? AND idx.maxY <= ?"
                ])
                sql = f"""
                    SELECT h.* FROM hotspots h
                    JOIN hotspots_rtree idx ON h.id = idx.id
                    {"WHERE " + " AND ".join(where) if where else ""}
                    ORDER BY h.frp DESC
                """
            else:
                sql = f"""
                    SELECT h.* FROM hotspots h
                    {"WHERE " + " AND ".join(where) if where else ""}
                    ORDER BY h.frp DESC
                """

            cursor = conn.execute(sql, params)
            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row["id"],
                    "event_id": row["event_id"],
                    "latitude": row["latitude"],
                    "longitude": row["longitude"],
                    "brightness": row["brightness"],
                    "confidence": row["confidence"],
                    "frp": row["frp"],
                    "acq_date": row["acq_date"]
                })
            return results
        finally:
            conn.close()

    @staticmethod
    def insert_batch(hotspots: List[Dict[str, Any]]) -> int:
        """Menyimpan sekumpulan data titik api satelit ke database."""
        if not hotspots:
            return 0

        with get_db() as conn:
            stmt = """
                INSERT INTO hotspots (event_id, latitude, longitude, brightness, confidence, frp, acq_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            rows = []
            for h in hotspots:
                evt = h.get("event_id", "national")
                lat = float(h.get("latitude") if "latitude" in h else h.get("lat", 0.0))
                lon = float(h.get("longitude") if "longitude" in h else h.get("lon", 0.0))
                b = float(h.get("brightness", 320.0))
                c = str(h.get("confidence", "nominal"))
                frp = float(h.get("frp", 15.0))
                date = str(h.get("acq_date", "2026-10-06"))
                rows.append((evt, lat, lon, b, c, frp, date))

            conn.executemany(stmt, rows)
            return len(rows)

    @staticmethod
    def count_all() -> int:
        """Menghitung total titik api aktif di database."""
        conn = get_db_connection()
        try:
            return conn.execute("SELECT COUNT(*) FROM hotspots").fetchone()[0]
        finally:
            conn.close()
