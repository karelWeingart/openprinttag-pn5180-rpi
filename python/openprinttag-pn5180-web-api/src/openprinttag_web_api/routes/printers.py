from openprinttag_web_api.models.api import Printer, PrinterListResponse,  PrinterCreate
from openprinttag_web_api.models.domain import PrinterRecord
from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated
from openprinttag_web_api.repositories.sqlite.printers import SqlitePrinterRepository
from openprinttag_web_api.services.printer_connection_service import PrinterConnectorService, get_printer_connector
import math

router = APIRouter(prefix="/printers", tags=["printers"])

@router.get("", response_model=PrinterListResponse)
async def get_printers(page: int, page_size: int,
                printer_repository: Annotated[SqlitePrinterRepository, 
                                              Depends(SqlitePrinterRepository)]) -> PrinterListResponse:
  _offset: int = (page - 1) * page_size
  _total: int = printer_repository.count()
  _printers: list[PrinterRecord] = printer_repository.list_all(offset=_offset, page_size=page_size)
  return PrinterListResponse(printers=[Printer.from_orm(_p) for _p in _printers], 
                            total=_total, 
                            total_pages=math.ceil(_total / page_size), 
                            page=page, 
                            page_size=page_size)

@router.post("", response_model=Printer)
async def add_printer(printer: PrinterCreate,
                printer_repository: Annotated[SqlitePrinterRepository, 
                                              Depends(SqlitePrinterRepository)]) -> Printer:
  _printer_id: int = printer_repository.save(printer)
  _printer: PrinterRecord | None = printer_repository.get_by_id(_printer_id)
  if not _printer:
    raise HTTPException(status_code=404, detail=f"Printer with id {_printer_id} not found after creation!")
  return Printer.from_orm(_printer)

@router.delete("/{printer_id}")
async def delete_printer(printer_id: int, 
                  printer_repository: Annotated[SqlitePrinterRepository, 
                                      Depends(SqlitePrinterRepository)]) -> Printer:
  _printer: PrinterRecord | None = printer_repository.get_by_id(printer_id)

  if not _printer:
    raise HTTPException(status_code=404, detail=f"Printer with id {printer_id} not found!")
  
  printer_repository.delete(printer_id)
  
  return Printer.from_orm(_printer)

@router.get("/{printer_id}", response_model=Printer)
async def get_printer(printer_id: int, 
                printer_repository: Annotated[SqlitePrinterRepository, 
                                      Depends(SqlitePrinterRepository)]) -> Printer:
  _printer: PrinterRecord | None = printer_repository.get_by_id(printer_id)
  if not _printer:
    raise HTTPException(status_code=404, detail=f"Printer with id {printer_id} not found!")
  return Printer.from_orm(_printer)

@router.post("/active/{printer_id}", response_model=Printer)
async def set_active_printer(printer_id: Annotated[int, Path(description="ID of the printer to set as active")],
                      printer_repository: Annotated[SqlitePrinterRepository, 
                                                    Depends(SqlitePrinterRepository)],
                      printer_connector: Annotated[PrinterConnectorService,
                                                  Depends(get_printer_connector)]) -> Printer:
  _printer: PrinterRecord | None = printer_repository.get_by_id(printer_id)
  _current_active_printer: PrinterRecord | None = printer_repository.get_by_status("ENABLED")
  if not _printer:
    raise HTTPException(status_code=404, detail=f"Printer with id {printer_id} not found!")
  _printer.status = "ENABLED"
  if _current_active_printer:
    _current_active_printer.status = "DISABLED"  
    printer_repository.update(_current_active_printer)
  printer_repository.update(_printer)

  await printer_connector.on_printer_enabled(_printer)
  
  return Printer.from_orm(_printer)

@router.get("/active/health", response_model=dict)
async def get_active_printer_health(
    printer_connector: Annotated[PrinterConnectorService,
                                Depends(get_printer_connector)]
) -> dict:
    return await printer_connector.get_health_status()
