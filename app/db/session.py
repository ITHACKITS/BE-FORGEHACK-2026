"""
app/db/session.py

Central SQLite connection handling with WAL mode
and R*Tree virtual tables for fast spatial queries.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from app.core.config import DATA_DIR

DB_PATH: Path = DATA_DIR / "standbai.db"


def get_db_connection() -> sqlite3.Connection:
    """
    Open a SQLite connection with production settings:
    WAL mode, 64 MB page cache and foreign keys on.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(
        str(DB_PATH),
        timeout=30.0,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row

    # Performance and integrity pragmas
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA cache_size = -64000;")  # 64MB memory page cache
    conn.execute("PRAGMA foreign_keys = ON;")

    return conn


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Transaction context manager: commits on success, rolls back on error.
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
