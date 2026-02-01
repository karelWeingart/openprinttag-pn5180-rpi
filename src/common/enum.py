from typing import Literal
from enum import Enum


class TagReadEvent(Enum):
    WELCOME = "welcome"
    SEARCHING = "searching"
    TAG_DETECTED = "detected"
    READING = "reading"
    BLOCK_UPLOADED = "block_uploaded"
    SUCCESS = "success"
    ERROR = "error"
    IDLE = "idle"


TagReadEventType = Literal[
    TagReadEvent.WELCOME,
    TagReadEvent.SEARCHING,
    TagReadEvent.TAG_DETECTED,
    TagReadEvent.READING,
    TagReadEvent.BLOCK_UPLOADED,
    TagReadEvent.SUCCESS,
    TagReadEvent.ERROR,
    TagReadEvent.IDLE,
]
