from common.api import register_callback
from common.enum import TagReadEvent
from models.event_dto import EventDto
from models.openprinttag_main import OpenPrintTagMain
from typing import Optional


def __on_tag_detected(event: EventDto) -> None:
    print(f"Tag detected with UID: {event.data.get('uid')}")


def __on_success(event: EventDto) -> None:
    tag_info: Optional[OpenPrintTagMain] = event.data.get("tag_info")
    if tag_info:
        print(f"Tag read successfully! {tag_info}")  # __str__() is called automatically
    else:
        print("Failed to read tag information.")


def __on_searching(event: EventDto) -> None:
    print("Searching for tags...", end="\r")


def __on_error(event: EventDto) -> None:
    _error = event.data.get("error", "Unknown error")
    print(f"Error reading tag: {_error}")


def __on_block_uploaded(event: EventDto) -> None:
    _block = event.data.get("block")
    _total_blocks = event.data.get("blocks")
    _percent = (_block / _total_blocks) * 100 if _total_blocks else 0
    _hashes = "#" * int(_percent / 5)
    print(f"Uploaded block: {_block} {_hashes}", end="\r")


def __on_welcome(event: EventDto) -> None:
    print("""
+==============================================================+
|                RPi/PN5180 OpenPrintTag Reader                |
|                 RFID Tag Reading Application                 |
+==============================================================+
    """)
    sensor = event.data.get("sensor", "Unknown")
    protocol = event.data.get("protocol", "Unknown")
    status = event.data.get("status", "Unknown")
    print("RFID Reader is ready.")
    print(f"Sensor: {sensor} | Protocol: {protocol} | Status: {status}")


def register_default_callbacks() -> None:
    """Register default callbacks for RFID events."""
    register_callback(TagReadEvent.WELCOME, __on_welcome)
    register_callback(TagReadEvent.TAG_DETECTED, __on_tag_detected)
    register_callback(TagReadEvent.SUCCESS, __on_success)
    register_callback(TagReadEvent.ERROR, __on_error)
    register_callback(TagReadEvent.SEARCHING, __on_searching)
    register_callback(TagReadEvent.BLOCK_UPLOADED, __on_block_uploaded)
