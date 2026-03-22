"""sqlite Repository for events table"""

from openprinttag_web_api.repositories.events import EventRepository
from openprinttag_web_api.models.domain import EventWithTag
from openprinttag_web_api.database import get_db
from typing import Optional, Any


class SqliteEventRepository(EventRepository):
    """SQLite implementation of event repository."""

    _EVENT_QUERY = """
        SELECT 
            e.id, 
            e.timestamp, 
            e.event_type, 
            e.success,
            e.tag_id,
            t.tag_uid,
            t.data AS tag_data
        FROM events e
        LEFT JOIN tags t ON t.id = e.tag_id
    """

    def _map(self, row: dict) -> EventWithTag:
        """Simple mapper"""
        return EventWithTag(
            id=row["id"],
            event_type=row["event_type"],
            timestamp=row["timestamp"],
            tag_id=row["tag_id"],
            success=bool(row["success"]),
            tag_uid=row["tag_uid"],
            tag_data=row["tag_data"],
        )

    def save(
        self,
        event_type: str,
        tag_id: Optional[int] = None,
        success: bool = True,
    ) -> int:
        """Save a new event."""
        with get_db() as db:
            cursor = db.execute(
                """
                INSERT INTO events (event_type, tag_id, success)
                VALUES (?, ?, ?)
                """,
                (event_type, tag_id, int(success)),
            )
            db.commit()
            return cursor.lastrowid or 0

    def get_by_id(self, event_id: int) -> Optional[EventWithTag]:
        """Get event by ID with tag data."""
        with get_db() as db:
            row = db.execute(
                f"{self._EVENT_QUERY} WHERE e.id = ?",
                (event_id,),
            ).fetchone()

            if row is None:
                return None

            return self._map(row)

    def list_all(
        self,
        page: int = 1,
        page_size: int = 50,
        event_type: Optional[str] = None,
        success: Optional[bool] = None,
    ) -> tuple[list[EventWithTag], int]:
        """List events with pagination and filters."""
        offset = (page - 1) * page_size
        conditions: list[str] = []
        params: list = []

        if event_type:
            conditions.append("e.event_type = ?")
            params.append(event_type)
        if success is not None:
            conditions.append("e.success = ?")
            params.append(int(success))

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        with get_db() as db:
            total = db.execute(
                f"SELECT COUNT(*) FROM events e {where}",
                params,
            ).fetchone()[0]

            rows = db.execute(
                f"{self._EVENT_QUERY} {where} ORDER BY e.timestamp DESC LIMIT ? OFFSET ?",
                params + [page_size, offset],
            ).fetchall()

        events = [self._map(row) for row in rows]
        return events, total

    def get_last_event_by_event_type(self, event_type: str) -> Optional[EventWithTag]:
        """Get last event by type"""
        _query = f"""{self._EVENT_QUERY} WHERE e.event_type = ?
                and e.timestamp = (SELECT MAX(b.timestamp) FROM events b 
                WHERE 
                e.event_type = b.event_type)"""
        with get_db() as db:
            _row = db.execute(_query, (event_type,)).fetchone()
            if _row is None:
                return None
            return self._map(_row)

    def get_by_tag_uid(self, tag_uid: str) -> list[EventWithTag]:
        """Get all events for a tag UID."""
        with get_db() as db:
            rows: list[Any] = db.execute(
                f"{self._EVENT_QUERY} WHERE t.tag_uid = ? ORDER BY e.timestamp DESC",
                (tag_uid,),
            ).fetchall()

        return [self._map(row) for row in rows]
