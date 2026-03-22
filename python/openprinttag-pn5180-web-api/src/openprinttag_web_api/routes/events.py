"""Event routes."""

from typing import Optional, Annotated

from fastapi import APIRouter, HTTPException, Path, Query, Depends

from openprinttag_web_api.models import EventDetailResponse, EventListResponse
from openprinttag_web_api.repositories.sqlite.events import SqliteEventRepository
from openprinttag_web_api.repositories.sqlite.filament_usage import (
    SqliteFilamentUsageRepository,
)

router = APIRouter(prefix="/events", tags=["events"])
_event_repo = SqliteEventRepository()


@router.get("", response_model=EventListResponse)
def list_events(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    success: Optional[bool] = Query(None, description="Filter by success/failure"),
):
    """List events with pagination and optional filters."""
    events, total = _event_repo.list_all(
        page=page,
        page_size=page_size,
        event_type=event_type,
        success=success,
    )

    return EventListResponse(
        events=[
            EventDetailResponse(
                id=e.id,
                event_type=e.event_type,
                timestamp=e.timestamp,
                tag_uid=e.tag_uid,
                success=e.success,
                tag_data=e.tag_data,
            )
            for e in events
        ],
        total=total,
        total_pages=(total + page_size - 1) // page_size,
        page=page,
        page_size=page_size,
    )


@router.get("/{event_id}", response_model=EventDetailResponse)
def get_event(event_id: int):
    """Get a single event by ID."""
    event = _event_repo.get_by_id(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventDetailResponse(
        id=event.id,
        event_type=event.event_type,
        timestamp=event.timestamp,
        tag_uid=event.tag_uid,
        success=event.success,
        tag_data=event.tag_data,
    )


@router.get("/latest/{event_type}", response_model=EventDetailResponse)
def get_last_event_by_event_type(
    event_type: Annotated[str, Path(description="Type of event to filter by")],
    event_repository: Annotated[SqliteEventRepository, Depends(SqliteEventRepository)],
):
    """Get the latest event by type."""
    event = event_repository.get_last_event_by_event_type(event_type)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventDetailResponse(
        id=event.id,
        event_type=event.event_type,
        timestamp=event.timestamp,
        tag_uid=event.tag_uid,
        success=event.success,
        tag_data=event.tag_data,
    )


@router.get("/{event_id}/filament", response_model=dict)
async def get_filament_usage_for_event(
    event_id: int,
    filament_usage_repository: Annotated[
        SqliteFilamentUsageRepository, Depends(SqliteFilamentUsageRepository)
    ],
    event_repository: Annotated[SqliteEventRepository, Depends(SqliteEventRepository)],
):
    """Get filament usage for a specific event."""
    _event = event_repository.get_by_id(event_id)
    if _event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    filament_usage: float = filament_usage_repository.get_total_usage_by_event_id(
        event_id
    )

    if filament_usage is None:
        raise HTTPException(
            status_code=404, detail="Filament usage not found for this event"
        )

    return {
        "event_id": event_id,
        "filament_usage": filament_usage,
        "tag_id": _event.tag_id,
    }
