from common.api import register_callback
from common.enum import TagReadEvent
from models.event_dto import EventDto
from models.openprinttag_main import OpenPrintTagMain
from typing import Optional


def __on_tag_detected(event: EventDto) -> None:
    print(f"Tag detected with UID: {event.data.get('uid')}")

def __on_success_read(event: EventDto) -> None:
    tag_info: Optional[OpenPrintTagMain] = event.data.get("tag_info")
    if tag_info:
        print(f"""
OpenPrintTag Data
===========================
    Material Name:          {tag_info.material_name}
    Material Type:          {tag_info.material_type}
    Material Class:         {tag_info.material_class}
    Manufacturer:           {tag_info.manufacturer}
    Short Material Name:    {tag_info.material_abbreviation}
    Max/Min Temp:           {tag_info.min_print_temperature}°C / {tag_info.max_print_temperature}°C
    Max/Min Bed:            {tag_info.min_bed_temperature}°C / {tag_info.max_bed_temperature}°C
===========================
""")
    else:
        print("Failed to read tag information.")

def __on_success_write(event: EventDto) -> None:
    print(f"Tag written... {event.data['uid']} - {event.data['bytes']}b")

def __on_cache_hit(event: EventDto) -> None:
    print("Returned from cache...")
    __on_success_read(event)

def __on_searching_read(event: EventDto) -> None:
    print("Searching for tags to read...", end="\r")

def __on_searching_write(event: EventDto) -> None:
    print("Searching for tags to write...", end="\r")


def __on_error(event: EventDto) -> None:
    _error = event.data.get("error", "Unknown error")
    print(f"Error reading tag: {_error}")

def __on_tag_uid_invalid(event: EventDto) -> None:
    _uid = event.data.get("uid", "Unknown UID")
    print(f"Invalid tag UID detected: {_uid}")


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
    register_callback(TagReadEvent.SUCCESS_READ, __on_success_read)
    register_callback(TagReadEvent.SUCCESS_WRITE, __on_success_write)
    register_callback(TagReadEvent.ERROR, __on_error)
    register_callback(TagReadEvent.SEARCHING_READ, __on_searching_read)
    register_callback(TagReadEvent.SEARCHING_WRITE, __on_searching_write)
    register_callback(TagReadEvent.BLOCK_UPLOADED, __on_block_uploaded)
    register_callback(TagReadEvent.CACHE_HIT, __on_cache_hit)
    register_callback(TagReadEvent.TAG_UID_INVALID, __on_tag_uid_invalid)