"""API request/response models (DTOs)."""

from typing import Optional

from pydantic import BaseModel

from openprinttag_shared.models.dto import TagDto
from openprinttag_shared.models.openprinttag_main import OpenPrintTagMain
from openprinttag_web_api.models.domain import PrinterRecord


# --- Tag models ---

class TagListResponse(BaseModel):
    """Paginated list of tags."""

    tags: list[TagDto]
    total: int
    total_pages: int
    page: int
    page_size: int


class TagBinResponse(BaseModel):
    """Response for bin file upload."""

    size: int
    file_name: str
    data: OpenPrintTagMain | None = None


# --- Event models ---

class EventResponse(BaseModel):
    """Single event returned by the API."""

    id: int
    event_type: str
    timestamp: str
    tag_uid: Optional[str] = None
    success: bool


class EventDetailResponse(EventResponse):
    """Event with inline tag data (returned by detail / joined queries)."""

    tag_data: Optional[str] = None


class EventListResponse(BaseModel):
    """Paginated list of events."""

    events: list[EventDetailResponse]
    total: int
    total_pages: int
    page: int
    page_size: int


# --- Printer models ---

class PrinterCreate(BaseModel):
    """Request model for creating/updating a printer."""

    name: str
    status: Optional[str] = None
    ip: Optional[str] = None
    token: Optional[str] = None


class Printer(PrinterCreate):
    """Printer with database ID."""

    id: int

    @classmethod
    def from_orm(cls, printer: PrinterRecord) -> "Printer":
        return cls(
            id=printer.id,
            name=printer.name,
            status=printer.status,
            ip=printer.ip,
            token=printer.token
        )


class PrinterListResponse(BaseModel):
    """Paginated list of printers."""

    printers: list[Printer]
    total: int
    total_pages: int
    page: int
    page_size: int
