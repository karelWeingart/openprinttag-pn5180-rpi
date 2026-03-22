from pydantic import BaseModel
from openprinttag_shared.models.dto import TagDto, ErrorDto, CompletedJobDto


class EventMessage(BaseModel):
    """Model for the MQTT event message payload.
    This one is used for generating messages sent by the pn5180 reader
    that are consumed by the web API.
    """

    event_type: str
    error: ErrorDto | None = None
    tag: TagDto | None = None


class FilamentUsageDto(BaseModel):
    tag_uid: str
    job_data: CompletedJobDto
