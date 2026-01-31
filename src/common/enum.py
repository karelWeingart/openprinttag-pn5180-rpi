from typing import Literal
from enum import Enum

class TagReadEvent(Enum):
    SEARCHING = "searching"
    TAG_DETECTED = "detected"
    READING = "reading"
    SUCCESS = "success"
    ERROR = "error"
    IDLE = "idle"                

TagReadEventType = Literal[
    TagReadEvent.SEARCHING,
    TagReadEvent.TAG_DETECTED,
    TagReadEvent.READING,
    TagReadEvent.SUCCESS,
    TagReadEvent.ERROR,
    TagReadEvent.IDLE
]