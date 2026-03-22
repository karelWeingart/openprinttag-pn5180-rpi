"""Domain models for business entities."""

from typing import Optional

from pydantic import BaseModel


class FilamentUsageRecord(BaseModel):
    """A single filament usage record."""
    
    id: int
    event_id: int
    job_id: int
    job_status: Optional[str] = None
    filament_usage: float  # in grams
    timestamp: str


class TagRecord(BaseModel):
    """A tag record from database."""
    
    id: int
    tag_uid: str
    data: str  # JSON string of tag data


class EventRecord(BaseModel):
    """An event record from database."""
    
    id: int
    event_type: str
    timestamp: str
    tag_id: Optional[int] = None
    success: bool = True


class EventWithTag(EventRecord):
    """Event with joined tag data."""
    
    tag_uid: Optional[str] = None
    tag_data: Optional[str] = None

class PrinterRecord(BaseModel):
    """Printer data."""
    id: int
    name: str
    status: Optional[str]
    ip: Optional[str]
    token: Optional[str]