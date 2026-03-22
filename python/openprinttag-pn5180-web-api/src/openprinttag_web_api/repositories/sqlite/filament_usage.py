"""Sqlite simple repository for filamentusage data."""

from openprinttag_web_api.database import get_db
from typing import Optional
from openprinttag_web_api.models.domain import FilamentUsageRecord
from openprinttag_web_api.repositories.filament_usage import FilamentUsageRepository


class SqliteFilamentUsageRepository(FilamentUsageRepository):
    """SQLite implementation of filament usage repository."""

    def save(
        self,
        event_id: int,
        job_id: int,
        filament_g: float,
        tag_id: int,
        job_status: Optional[str] = None,
    ) -> int:
        """Save filament usage record."""
        with get_db() as db:
            cursor = db.execute(
                """
                INSERT INTO filament_usage (event_id, job_id, filament_usage, job_status, tag_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (event_id, job_id, filament_g, job_status, tag_id),
            )
            db.commit()
            return cursor.lastrowid or 0

    def get_usage_by_event(self, event_id: int) -> Optional[FilamentUsageRecord]:
        """Get usage record by event ID."""
        with get_db() as db:
            row = db.execute(
                """
                SELECT id, event_id, job_id, job_status, filament_usage, timestamp
                FROM filament_usage
                WHERE event_id = ?
                """,
                (event_id,),
            ).fetchone()

            if row is None:
                return None

            return FilamentUsageRecord(
                id=row["id"],
                event_id=row["event_id"],
                job_id=row["job_id"],
                job_status=row["job_status"],
                filament_usage=row["filament_usage"],
                timestamp=row["timestamp"],
            )

    def get_total_usage_by_tag_uid(self, tag_uid: str) -> float:
        """Get total filament usage for a tag/spool."""
        with get_db() as db:
            row = db.execute(
                """
                SELECT COALESCE(SUM(fu.filament_usage), 0) as total
                FROM filament_usage fu
                JOIN events e ON fu.event_id = e.id
                JOIN tags t ON e.tag_id = t.id
                WHERE t.tag_uid = ?
                """,
                (tag_uid,),
            ).fetchone()

            return float(row["total"]) if row else 0.0

    def get_total_usage_by_event_id(self, event_id: int) -> float:
        """Get total filament usage for a tag/spool."""
        with get_db() as db:
            row = db.execute(
                """
                SELECT COALESCE(SUM(fu.filament_usage), 0) as total
                FROM filament_usage fu
                WHERE fu.event_id = ?
                """,
                (event_id,),
            ).fetchone()

            return float(row["total"]) if row else 0.0

    def get_remaining_filament(self, tag_uid: str, initial_weight_g: float) -> float:
        """Get remaining filament on spool."""
        used = self.get_total_usage_by_tag_uid(tag_uid)
        return max(0.0, initial_weight_g - used)
