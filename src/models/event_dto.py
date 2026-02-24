""" EventDto - used for transfer data from event trigers to callbacks. """
from pydantic import BaseModel
from common.enum import TagReadEventType
from typing import Optional, Any


class EventDto(BaseModel):
    event_type: TagReadEventType
    data: dict[str, Any] = {}
