"""SQLite database setup and access."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

DB_PATH = Path.home() / ".openprinttag" / "events.db"


def init_db() -> None:
    """Initialize the database with required tables and indexes."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_db() as db:
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA foreign_keys=ON")
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS tags (
                tag_uid TEXT PRIMARY KEY,
                material_type TEXT,
                manufacturer TEXT,
                color TEXT,
                name TEXT
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                tag_uid TEXT,
                success INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (tag_uid) REFERENCES tags (tag_uid)
            )
            """
        )
        db.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_events_type ON events (event_type)
            """
        )
        db.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events (timestamp)
            """
        )
        db.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_events_tag_uid ON events (tag_uid)
            """
        )
        db.commit()


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Get a database connection with row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
