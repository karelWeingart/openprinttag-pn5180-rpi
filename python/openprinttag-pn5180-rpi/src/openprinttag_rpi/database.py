import sqlite3
from contextlib import contextmanager
from typing import Generator
from openprinttag_shared.config import DATA_ROOT_FOLDER_PATH



DB_PATH = DATA_ROOT_FOLDER_PATH / "pn5180_data.db"

def init_db() -> None:
  DB_PATH.parent.mkdir(parents=True, exist_ok=True)
  with get_db() as db:
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("""
            CREATE TABLE IF NOT EXISTS filament_usage_message (                
                tag_uid TEXT NOT NULL,
                job_id INTEGER NOT NULL,
                filament_usage FLOAT NOT NULL,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                status TEXT NOT NULL DEFAULT ('NOT_PROCESSED'),
                PRIMARY KEY(job_id, tag_uid)
            )
        """)

@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Get a database connection with row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()