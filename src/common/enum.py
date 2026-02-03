from typing import Literal
from enum import Enum


class TagReadEvent(Enum):
    WELCOME = "welcome"
    SEARCHING = "searching"
    CACHE_HIT = "cache_hit"
    TAG_DETECTED = "detected"
    READING = "reading"
    BLOCK_UPLOADED = "block_uploaded"
    SUCCESS = "success"
    ERROR = "error"
    IDLE = "idle"


TagReadEventType = Literal[
    TagReadEvent.WELCOME,
    TagReadEvent.SEARCHING,
    TagReadEvent.CACHE_HIT,
    TagReadEvent.TAG_DETECTED,
    TagReadEvent.READING,
    TagReadEvent.BLOCK_UPLOADED,
    TagReadEvent.SUCCESS,
    TagReadEvent.ERROR,
    TagReadEvent.IDLE,
]
