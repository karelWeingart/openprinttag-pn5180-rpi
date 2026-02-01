from pydantic import BaseModel
from common.enum import TagReadEventType
from typing import Optional, Any


class EventDto(BaseModel):
    event_type: TagReadEventType
    data: Optional[dict[str, Any]] = None
