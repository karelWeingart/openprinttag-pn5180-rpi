"""Tag routes."""

import logging
from fastapi import APIRouter, HTTPException, Query, UploadFile, File

from openprinttag_web_api.database import get_db
from openprinttag_web_api.mqtt.publisher import publish_openprinttag_data
from openprinttag_web_api.models import TagBinResponse, TagListResponse
from openprinttag_shared.openprinttag.parser import parse_openprinttag
from openprinttag_shared.models.openprinttag_main import OpenPrintTagMain
from openprinttag_shared.models.dto import TagDto

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=TagListResponse)
async def list_tags(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
):
    """List all known tags with pagination."""
    offset = (page - 1) * page_size

    with get_db() as db:
        total = db.execute("SELECT COUNT(DISTINCT tag_uid) FROM tags").fetchone()[0]

        rows = db.execute(
            """
            SELECT t.tag_uid, t.data FROM tags t
            INNER JOIN (
                SELECT tag_uid, MAX(id) AS max_id FROM tags GROUP BY tag_uid
            ) latest ON t.id = latest.max_id
            ORDER BY t.tag_uid LIMIT ? OFFSET ?
            """,
            [page_size, offset],
        ).fetchall()

    tags = [TagDto.model_validate_json(row["data"]) for row in rows]

    return TagListResponse(
        tags=tags,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{tag_uid}/event/{event_id}", response_model=TagDto)
async def get_tag(tag_uid: str, event_id: int):
    """Get tag data associated with a specific event."""
    with get_db() as db:
        row = db.execute(
            """
            SELECT t.data FROM tags t
            JOIN events e ON e.tag_id = t.id
            WHERE t.tag_uid = ? AND e.id = ?
            """,
            [tag_uid, event_id],
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return TagDto.model_validate_json(row["data"])


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
