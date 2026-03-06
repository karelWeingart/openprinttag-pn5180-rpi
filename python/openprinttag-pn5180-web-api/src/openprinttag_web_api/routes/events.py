"""Event routes."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from openprinttag_web_api.database import get_db
from openprinttag_web_api.models import EventDetailResponse, EventListResponse

router = APIRouter(prefix="/events", tags=["events"])

_EVENT_QUERY = """
    SELECT 
        e.id, 
        e.timestamp, 
        e.event_type, 
        e.success,
        e.tag_uid
    FROM events e
"""


@router.get("", response_model=EventListResponse)
def list_events(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    success: Optional[bool] = Query(None, description="Filter by success/failure"),
):
    """List events with pagination and optional filters."""
    _offset = (page - 1) * page_size
    _conditions: list[str] = []
    _params: list = []

    if event_type:
        _conditions.append("e.event_type = ?")
        _params.append(event_type)
    if success:
        _conditions.append("e.success = ?")
        _params.append(int(success))

    _where = f"WHERE {' AND '.join(_conditions)}" if _conditions else ""

    with get_db() as _db:
        _total = _db.execute(
            f"SELECT COUNT(*) FROM events e {_where}", _params
        ).fetchone()[0]

        _rows = _db.execute(
            f"{_EVENT_QUERY} {_where} ORDER BY e.timestamp DESC LIMIT ? OFFSET ?",
            _params + [page_size, _offset],
        ).fetchall()

    _events = [
        EventDetailResponse(**{k: _row[k] for k in _row.keys()}) for _row in _rows
    ]

    return EventListResponse(
        events=_events,
        total=_total,
        total_pages=(_total + page_size - 1) // page_size,
        page=page,
        page_size=page_size,
    )


@router.get("/{event_id}", response_model=EventDetailResponse)
def get_event(event_id: int):
    """Get a single event by ID."""
    with get_db() as _db:
        _row = _db.execute(f"{_EVENT_QUERY} WHERE e.id = ?", [event_id]).fetchone()
    if _row is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventDetailResponse(**{k: _row[k] for k in _row.keys()})
