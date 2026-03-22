"""SQLite database setup and access."""

import sqlite3
from contextlib import contextmanager

from typing import Generator
from openprinttag_shared.config import DATA_ROOT_FOLDER_PATH

DB_PATH = DATA_ROOT_FOLDER_PATH / "events.db"


def init_db() -> None:
    """Initialize the database with required tables and indexes."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_db() as db:
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA foreign_keys=ON")
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_uid TEXT NOT NULL,
                data TEXT NOT NULL,
                UNIQUE(tag_uid, data)
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                tag_id INTEGER,
                success INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (tag_id) REFERENCES tags (id)
            )
            """
        )
        db.execute("""
            CREATE TABLE IF NOT EXISTS filament_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                job_id INTEGER NOT NULL,
                job_status TEXT,
                filament_usage FLOAT NOT NULL,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                tag_id INTEGER NOT NULL,
                FOREIGN KEY (event_id) REFERENCES events (id),
                FOREIGN KEY (tag_id) REFERENCES tags (id)
            )
        """)
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
            CREATE INDEX IF NOT EXISTS idx_events_tag_id ON events (tag_id)
            """
        )
        db.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_tags_tag_uid ON tags (tag_uid)
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS printers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                status TEXT,
                ip TEXT,
                token TEXT
            )
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
