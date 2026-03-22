"""Sqlite tags repository."""

from openprinttag_web_api.repositories.tags import TagRepository
from openprinttag_web_api.database import get_db
from typing import Optional
from openprinttag_web_api.models.domain import TagRecord


class SqliteTagRepository(TagRepository):
    """SQLite implementation of tag repository."""

    def save(self, tag_uid: str, data: str) -> int:
        """Save or update tag data."""
        with get_db() as db:
            cursor = db.execute(
                """
                INSERT INTO tags (tag_uid, data)
                VALUES (?, ?)
                ON CONFLICT(tag_uid, data) DO UPDATE SET data = excluded.data
                """,
                (tag_uid, data),
            )
            db.commit()
            return cursor.lastrowid or 0

    def get_by_uid(self, tag_uid: str) -> Optional[TagRecord]:
        """Get latest tag data by UID."""
        with get_db() as db:
            row = db.execute(
                """
                SELECT id, tag_uid, data
                FROM tags
                WHERE tag_uid = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (tag_uid,),
            ).fetchone()

            if row is None:
                return None

            return TagRecord(
                id=row["id"],
                tag_uid=row["tag_uid"],
                data=row["data"],
            )

    def get_by_id(self, tag_id: int) -> Optional[TagRecord]:
        """Get tag by database ID."""
        with get_db() as db:
            row = db.execute(
                "SELECT id, tag_uid, data FROM tags WHERE id = ?",
                (tag_id,),
            ).fetchone()

            if row is None:
                return None

            return TagRecord(
                id=row["id"],
                tag_uid=row["tag_uid"],
                data=row["data"],
            )

    def list_all(
        self,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[TagRecord], int]:
        """List all tags with pagination (latest version of each)."""
        offset = (page - 1) * page_size

        with get_db() as db:
            total = db.execute("SELECT COUNT(DISTINCT tag_uid) FROM tags").fetchone()[0]

            rows = db.execute(
                """
                SELECT t.id, t.tag_uid, t.data
                FROM tags t
                INNER JOIN (
                    SELECT tag_uid, MAX(id) AS max_id FROM tags GROUP BY tag_uid
                ) latest ON t.id = latest.max_id
                ORDER BY t.tag_uid
                LIMIT ? OFFSET ?
                """,
                (page_size, offset),
            ).fetchall()

        tags = [
            TagRecord(id=row["id"], tag_uid=row["tag_uid"], data=row["data"])
            for row in rows
        ]
        return tags, total

    def count_unique(self) -> int:
        """Count unique tag UIDs."""
        with get_db() as db:
            return db.execute("SELECT COUNT(DISTINCT tag_uid) FROM tags").fetchone()[0]
