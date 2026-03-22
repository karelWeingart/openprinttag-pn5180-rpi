"""Tag routes."""

import logging
import math
from fastapi import APIRouter, HTTPException, Query, UploadFile, File

from openprinttag_web_api.integrations.mqtt.bin_publisher import (
    publish_openprinttag_data,
)
from openprinttag_web_api.models import TagBinResponse, TagListResponse
from openprinttag_web_api.repositories.sqlite.tags import SqliteTagRepository
from openprinttag_web_api.repositories.sqlite.events import SqliteEventRepository
from openprinttag_shared.openprinttag.parser import parse_openprinttag
from openprinttag_shared.models.openprinttag_main import OpenPrintTagMain
from openprinttag_shared.models.dto import TagDto

router = APIRouter(prefix="/tags", tags=["tags"])
_tag_repo = SqliteTagRepository()
_event_repo = SqliteEventRepository()


@router.get("", response_model=TagListResponse)
async def list_tags(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
):
    """List all known tags with pagination."""
    tags_records, total = _tag_repo.list_all(page=page, page_size=page_size)
    tags = [TagDto.model_validate_json(record.data) for record in tags_records]

    return TagListResponse(
        tags=tags,
        total=total,
        total_pages=math.ceil(total / page_size),
        page=page,
        page_size=page_size,
    )


@router.get("/{tag_uid}/event/{event_id}", response_model=TagDto)
async def get_tag(tag_uid: str, event_id: int):
    """Get tag data associated with a specific event."""
    event = _event_repo.get_by_id(event_id)
    if event is None or event.tag_uid != tag_uid or event.tag_data is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return TagDto.model_validate_json(event.tag_data)


@router.delete("/bin")
async def delete_tag_bin_file() -> None:
    if not publish_openprinttag_data(b"cancel"):
        raise HTTPException(
            status_code=500, detail="Failed to cancel bin file writing..."
        )


@router.post("/bin", response_model=TagBinResponse)
async def upload_tag_bin_file(file: UploadFile = File(...)) -> TagBinResponse:
    """Upload a binary file containing tag data."""
    _raw_data = await file.read()
    logging.warning(
        f"Received bin file upload: {file.filename}... Size: {len(_raw_data)} bytes"
    )
    _main: OpenPrintTagMain | None = None

    try:
        _, _main, _ = parse_openprinttag(_raw_data)
    except ValueError as e:
        logging.error(f"Failed to decode OpenPrintTag data from uploaded file: {e}")
        raise HTTPException(
            status_code=400, detail=f"Failed to decode OpenPrintTag data: {e}"
        ) from e

    if publish_openprinttag_data(_raw_data):
        _filename = file.filename if file.filename else "unknown.bin"
        return TagBinResponse(size=len(_raw_data), file_name=_filename, data=_main)
    else:
        raise HTTPException(
            status_code=500, detail="Failed to publish bin file to MQTT"
        )
