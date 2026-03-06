"""Tag routes."""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File

from openprinttag_web_api.database import get_db
from openprinttag_web_api.mqtt.publisher import publish_openprinttag_data
from openprinttag_web_api.models import TagBinResponse, TagListResponse, TagResponse

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=TagListResponse)
def list_tags(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
):
    """List all known tags with pagination."""
    offset = (page - 1) * page_size

    with get_db() as db:
        total = db.execute("SELECT COUNT(*) FROM tags").fetchone()[0]

        rows = db.execute(
            "SELECT * FROM tags ORDER BY tag_uid LIMIT ? OFFSET ?",
            [page_size, offset],
        ).fetchall()

    tags = [TagResponse(**{k: row[k] for k in row.keys()}) for row in rows]

    return TagListResponse(
        tags=tags,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{tag_uid}", response_model=TagResponse)
def get_tag(tag_uid: str):
    """Get a single tag by UID."""
    with get_db() as db:
        row = db.execute("SELECT * FROM tags WHERE tag_uid = ?", [tag_uid]).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return TagResponse(**{k: row[k] for k in row.keys()})


@router.post("/bin", response_model=TagBinResponse)
async def upload_tag_bin_file(file: UploadFile = File(...)) -> TagBinResponse:
    """Upload a binary file containing tag data."""
    _data = await file.read()
    if publish_openprinttag_data(_data):
        return TagBinResponse(size=len(_data))
    else:
        raise HTTPException(
            status_code=500, detail="Failed to publish bin file to MQTT"
        )
