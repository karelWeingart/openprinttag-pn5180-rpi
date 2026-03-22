from abc import ABC, abstractmethod
from openprinttag_web_api.models.api import PrinterCreate, Printer
from openprinttag_web_api.models.domain import PrinterRecord
from openprinttag_web_api.database import get_db

class PrinterRepository(ABC):
  """ Interface for PrinterRepository """
  _sql_table: str = "printers"

  @abstractmethod
  def save(self, printer: PrinterCreate) -> int:
    """
    inserts a new printer.
    """
  
  @abstractmethod
  def delete(self, printer_id: int) -> None:
    """ Deletes printer

    Args:
        printer_id (int): id of printer in db.
    """

  @abstractmethod
  def list_all(self,
              offset: int = 0,
              page_size: int = 50) -> list[PrinterRecord]:
    """Paginated list all printers"""
  
  @abstractmethod
  def update(self, printer: PrinterRecord) -> PrinterRecord:
    """Update printer"""

  @abstractmethod
  def get_by_id(self, printer_id: int) -> PrinterRecord | None:
    """Get printer by id"""

  @abstractmethod
  def get_by_status(self, status: str) -> PrinterRecord | None:
    """Get printer by status"""

  def count(self) -> int:
    with get_db() as db:
      _cursor = db.execute(f"SELECT count(*) FROM {self._sql_table}")
      return _cursor.rowcount
