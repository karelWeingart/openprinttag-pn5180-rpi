"""Pydantic models for the web API."""

from typing import Optional

from pydantic import BaseModel


# ── Tag models ──────────────────────────────────────────────


class TagBase(BaseModel):
    """Shared tag fields."""

    tag_uid: str
    material_type: Optional[str] = None
    manufacturer: Optional[str] = None
    color: Optional[str] = None
    name: Optional[str] = None


class TagResponse(TagBase):
    """Tag returned by the API."""

    pass


class TagListResponse(BaseModel):
    """Paginated list of tags."""

    tags: list[TagResponse]
    total: int
    page: int
    page_size: int

class TagBinResponse(BaseModel):
    """ Response for bin file upload. """

    size: int


class EventResponse(BaseModel):
    """Single event returned by the API."""

    id: int
    event_type: str
    timestamp: str
    tag_uid: Optional[str] = None
    success: bool


class EventDetailResponse(EventResponse):
    """Event with inline tag data (returned by detail / joined queries)."""

    material: Optional[str] = None
    manufacturer: Optional[str] = None
    color: Optional[str] = None
    min_temp: Optional[int] = None
    max_temp: Optional[int] = None
    data: Optional[str] = None


class EventListResponse(BaseModel):
    """Paginated list of events."""

    events: list[EventResponse]
    total: int
    total_pages: int
    page: int
    page_size: int
