from pydantic import BaseModel
from openprinttag_shared.models.openprinttag_main import OpenPrintTagMain


class TagDto(OpenPrintTagMain):
    """Tag returned by the API."""

    tag_uid: str | None = None


class ErrorDto(BaseModel):
    """Model for error messages sent by the pn5180 reader."""

    error: str
    tag_uid: str | None = None

class CompletedJobDto(BaseModel):
    """Data yielded when a print job completes."""
    
    job_id: int
    file_name: str
    filament_type: str | None = None
    total_filament_g: float | None = None
    used_filament_g: float | None = None
    final_progress: float
    end_reason: str
