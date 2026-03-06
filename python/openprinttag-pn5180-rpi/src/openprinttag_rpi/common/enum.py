"""Enums definitions."""

from typing import Literal
from enum import Enum


class TagReadEvent(Enum):
    WELCOME = "welcome"
    SEARCHING_READ = "searching_read"
    SEARCHING_WRITE = "searching_write"
    CACHE_HIT = "cache_hit"
    TAG_DETECTED = "detected"
    TAG_UID_INVALID = "tag_uid_invalid"
    READING = "reading"
    BLOCK_UPLOADED = "block_uploaded"
    BLOCK_WRITTEN = "block_written"
    SUCCESS_READ = "success_read"
    SUCCESS_WRITE = "success_write"
    ERROR = "error"
    IDLE = "idle"


TagReadEventType = Literal[
    TagReadEvent.WELCOME,
    TagReadEvent.SEARCHING_READ,
    TagReadEvent.SEARCHING_WRITE,
    TagReadEvent.CACHE_HIT,
    TagReadEvent.TAG_DETECTED,
    TagReadEvent.TAG_UID_INVALID,
    TagReadEvent.READING,
    TagReadEvent.BLOCK_UPLOADED,
    TagReadEvent.BLOCK_WRITTEN,
    TagReadEvent.SUCCESS_READ,
    TagReadEvent.SUCCESS_WRITE,
    TagReadEvent.ERROR,
    TagReadEvent.IDLE,
]
