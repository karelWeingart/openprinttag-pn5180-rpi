from openprinttag_web_api.repositories.printers import PrinterRepository
from openprinttag_web_api.database import get_db
from openprinttag_web_api.models.api import PrinterCreate
from openprinttag_web_api.models.domain import PrinterRecord


class SqlitePrinterRepository(PrinterRepository):
    def save(self, printer: PrinterCreate) -> int:
        with get_db() as db:
            cursor = db.execute(
                "INSERT INTO printers (name, status, ip, token) VALUES (?, ?, ?, ?)",
                (printer.name, "DISABLED", printer.ip, printer.token),
            )
            db.commit()
            printer_id = cursor.lastrowid or 0
            return printer_id

    def get_by_status(self, status: str) -> PrinterRecord | None:
        with get_db() as db:
            row = db.execute(
                f"SELECT id, name, status, ip, token FROM {self._sql_table} WHERE status = ?",
                (status,),
            ).fetchone()
            if row is None:
                return None
            return PrinterRecord(
                id=row["id"],
                name=row["name"],
                status=row["status"],
                ip=row["ip"],
                token=row["token"],
            )

    def get_by_id(self, printer_id) -> PrinterRecord | None:
        with get_db() as db:
            row = db.execute(
                f"SELECT id, name, status, ip, token FROM {self._sql_table} WHERE id = ?",
                (printer_id,),
            ).fetchone()
            if row is None:
                return None
            return PrinterRecord(
                id=row["id"],
                name=row["name"],
                status=row["status"],
                ip=row["ip"],
                token=row["token"],
            )

    def delete(self, printer_id: int) -> None:
        with get_db() as db:
            db.execute(
                f"DELETE FROM {self._sql_table} WHERE id = ?",
                (printer_id,),
            )
            db.commit()

    def list_all(self, offset: int = 0, page_size: int = 50) -> list[PrinterRecord]:
        with get_db() as db:
            _rows = db.execute(
                f"""SELECT id,
                          name, 
                          status, 
                          ip, 
                          token 
                        FROM {self._sql_table} 
                        ORDER BY id DESC LIMIT ? OFFSET ?""",
                (
                    page_size,
                    offset,
                ),
            ).fetchall()
            _printers = [
                PrinterRecord(
                    id=_row["id"],
                    name=_row["name"],
                    status=_row["status"],
                    ip=_row["ip"],
                    token=_row["token"],
                )
                for _row in _rows
            ]
            return _printers

    def update(self, printer: PrinterRecord) -> PrinterRecord:
        with get_db() as db:
            _cursor = db.execute(
                f"""UPDATE {self._sql_table} 
                        SET 
                          status = ?,
                          ip = ?,
                          name = ?,
                          token = ?
                        WHERE id = ?""",
                (
                    printer.status,
                    printer.ip,
                    printer.name,
                    printer.token,
                    printer.id,
                ),
            )
            if _cursor.rowcount != 1:
                raise ValueError(f"Expected 1 row updated, got {_cursor.rowcount}")
            db.commit()
            return printer
