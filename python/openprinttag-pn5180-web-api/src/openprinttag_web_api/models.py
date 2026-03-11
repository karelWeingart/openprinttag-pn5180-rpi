"""Pydantic models for the web API."""

from typing import Optional

from pydantic import BaseModel

from openprinttag_shared.models.dto import TagDto
from openprinttag_shared.models.openprinttag_main import OpenPrintTagMain


class TagListResponse(BaseModel):
    """Paginated list of tags."""

    tags: list[TagDto]
    total: int
    page: int
    page_size: int


class TagBinResponse(BaseModel):
    """Response for bin file upload."""

    size: int
    file_name: str
    data: OpenPrintTagMain | None = None


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
