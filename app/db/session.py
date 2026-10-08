"""
app/db/session.py

Manajemen koneksi database SQLite terpusat dengan optimasi WAL mode
dan dukungan virtual table R*Tree untuk kueri spasial ultra-cepat.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from app.core.config import DATA_DIR

DB_PATH: Path = DATA_DIR / "udarasiaga.db"


def get_db_connection() -> sqlite3.Connection:
    """
    Membuka koneksi ke SQLite database dengan pengaturan performa produksi.
    WAL mode, cache 64MB, dan foreign keys aktif.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(
        str(DB_PATH),
        timeout=30.0,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row

    # Optimasi performa dan integritas database
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA cache_size = -64000;")  # 64MB memory page cache
    conn.execute("PRAGMA foreign_keys = ON;")

    return conn


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager untuk transaksi database dengan auto-commit dan rollback aman.
    """
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
