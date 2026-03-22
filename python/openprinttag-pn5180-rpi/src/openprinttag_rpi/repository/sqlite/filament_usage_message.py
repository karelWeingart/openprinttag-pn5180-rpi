from openprinttag_rpi.models.domain import FilamentUsageMessage
from openprinttag_rpi.repository.filament_usage_message import (
    FilamentUsageMessageRepository,
)
from openprinttag_rpi.database import get_db
import sqlite3


class SqliteFilamentUsageMessageRepository(FilamentUsageMessageRepository):
    def save(
        self,
        job_id: str,
        tag_uid: str,
        filament_usage: float,
        status: str = "NOT_PROCESSED",
    ) -> int:
        with get_db() as db:
            _cursor: sqlite3.Cursor = db.execute(
                f""" INSERT INTO {self._sql_table}
                  (job_id, tag_uid, filament_usage, status)
                VALUES (?, ?, ?, ?)           
                """,
                (
                    job_id,
                    tag_uid,
                    filament_usage,
                    status,
                ),
            )
            return _cursor.lastrowid or 0

    def find_by_status_and_by_tag_uid(
        self, tag_uid: str, status: str = "NOT_PROCESSED"
    ) -> list[FilamentUsageMessage]:
        with get_db() as db:
            _cursor: sqlite3.Cursor = db.execute(
                f""" SELECT * FROM {self._sql_table}
                  WHERE tag_uid = ? AND status = ? ORDER BY timestamp DESC
                """,
                (tag_uid, status),
            )
            _rows: list[dict] = _cursor.fetchall()
            return [FilamentUsageMessage(**row) for row in _rows]

    def update(
        self, filament_usage_message: FilamentUsageMessage
    ) -> FilamentUsageMessage:
        with get_db() as db:
            db.execute(
                f""" UPDATE {self._sql_table}
                  SET status = ?,
                  timestamp = ?,
                  filament_usage = ?
                  WHERE job_id = ? AND tag_uid = ?
                """,
                (
                    filament_usage_message.status,
                    filament_usage_message.timestamp,
                    filament_usage_message.filament_usage,
                    filament_usage_message.job_id,
                    filament_usage_message.tag_uid,
                ),
            )
            return filament_usage_message

    def get_usage_by_tag_uid_status(
        self, tag_uid: str, status: str = "NOT_PROCESSED"
    ) -> float:
        with get_db() as db:
            _cursor: sqlite3.Cursor = db.execute(
                f""" SELECT sum(filament_usage) as filament_usage FROM {self._sql_table}
                  WHERE tag_uid = ? AND status = ? ORDER BY timestamp DESC
                """,
                (tag_uid, status),
            )
            _row: dict = _cursor.fetchone()
            return (
                _row["filament_usage"]
                if _row and _row["filament_usage"] is not None
                else 0.0
            )
