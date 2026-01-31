from pydantic import BaseModel
from common.enum import TagReadEventType

class EventDto(BaseModel):
    event_type: TagReadEventType
    data: dict | None = None