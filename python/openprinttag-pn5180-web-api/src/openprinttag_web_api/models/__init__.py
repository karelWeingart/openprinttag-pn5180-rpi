"""Models package for OpenPrintTag Web API."""

from openprinttag_web_api.models.api import (
    EventDetailResponse,
    EventListResponse,
    EventResponse,
    PrinterCreate,
    Printer,
    PrinterListResponse,
    TagBinResponse,
    TagListResponse,
)
from openprinttag_web_api.models.domain import (
    EventRecord,
    EventWithTag,
    FilamentUsageRecord,
    TagRecord,
)
# GcodeMetadata stays in integrations/printer/bgcode.py (tightly coupled with parser)

__all__ = [
    # API models
    "EventDetailResponse",
    "EventListResponse",
    "EventResponse",
    "PrinterCreate",
    "Printer",
    "PrinterListResponse",
    "TagBinResponse",
    "TagListResponse",
    # Domain models
    "EventRecord",
    "EventWithTag",
    "FilamentUsageRecord",
    "TagRecord",
]
