"""reader module - that initializes sensor and reading thread
S"""

from threading import Thread
from typing import Any, Literal
from openprinttag_rpi.pn5180_rpi.sensor import (
    ExtendedISO15693Sensor,
    CommandError,
    PostCommandError,
    PreCommandError,
)
from openprinttag_rpi.models.event_dto import EventDto
from openprinttag_rpi.repository.sqlite.filament_usage_message import (
    SqliteFilamentUsageMessageRepository,
)
from openprinttag_rpi.service import filament_usage as _filament_usage
from openprinttag_shared.models.dto import TagDto
from openprinttag_shared.openprinttag.parser import parse_openprinttag
from openprinttag_rpi.integrations.mqtt.tag_write_queue import (
    get_openprinttag_bin,
    has_openprinttag_bin,
)
import pigpio  # type: ignore[import-untyped]
import time
from openprinttag_rpi.common.api import TagReadEvent, get_queue_size, register_event
from openprinttag_shared.models.openprinttag_main import OpenPrintTagMain

_SEARCHING_DELAY = 0.1
_SEARCHING_READ_EVENT_INTERVAL = 5.0
_SEARCHING_WRITE_EVENT_INTERVAL = 1.0
_AFTER_READ_DELAY = 2

_TAG_CACHE_: dict[str, tuple[OpenPrintTagMain, float]] = {}
_TAG_CACHE_TTL: float = 120.0  # seconds

_filament_usage_message_repository = SqliteFilamentUsageMessageRepository()


def read_openprinttag(
    reader: ExtendedISO15693Sensor, num_blocks: int
) -> OpenPrintTagMain | None:
    """Reads OpenPrintTag data from the tag using the provided reader."""
    try:
        _data = reader.read_multi_blocks(num_blocks)
        return parse_openprinttag(_data)[1]
    except (CommandError, PreCommandError, PostCommandError, ValueError) as e:
        register_event(EventDto(event_type=TagReadEvent.ERROR, data={"error": str(e)}))
        return None


def __trigger_searching_event(
    start_time: float,
    search_type: Literal[TagReadEvent.SEARCHING_READ, TagReadEvent.SEARCHING_WRITE],
) -> float:
    """Trigger SEARCHING event at defined intervals."""
    current_time = time.time()
    interval = (
        _SEARCHING_READ_EVENT_INTERVAL
        if search_type == TagReadEvent.SEARCHING_READ
        else _SEARCHING_WRITE_EVENT_INTERVAL
    )

    if current_time - start_time >= interval:
        register_event(EventDto(event_type=search_type))
        return current_time
    return start_time


def _invalid(uid: str) -> bool:
    """Check if the UID is invalid."""

    if len(uid) < 16:
        return True

    if len(set(uid)) == 1:
        return True

    return False


def __put_cache(uid: str, tag_info: OpenPrintTagMain) -> None:
    """Put the UID and tag info into the recent cache."""
    _TAG_CACHE_[uid] = (tag_info, time.time())


def __in_cache(uid: str, force_delete: bool = False) -> bool:
    """Check if the UID is in the recent cache to avoid duplicate reads."""
    if uid in _TAG_CACHE_:
        if force_delete:
            del _TAG_CACHE_[uid]
            return False
        cached_time = _TAG_CACHE_[uid][1]
        cached_data = _TAG_CACHE_[uid][0]
        if time.time() - cached_time < _TAG_CACHE_TTL:
            register_event(
                EventDto(
                    event_type=TagReadEvent.CACHE_HIT, data={"tag_info": cached_data}
                )
            )
            return True
        else:
            del _TAG_CACHE_[uid]  # Remove stale cache entry
    return False


def get_number_blocks(reader: ExtendedISO15693Sensor) -> int:
    """Retrieve and parse system information from the tag.
    For now not blocking on errors to allow further reading attempts.
    """
    try:
        _info = reader.get_system_info()
        _info_dict: dict[str, Any] | None = None
        if _info:
            _info_dict = reader.parse_system_info(_info)
        if _info_dict:
            return _info_dict.get("num_blocks", 255)
        else:
            return 255
    except (CommandError, PreCommandError, PostCommandError):
        # register_event(EventDto(event_type=TagReadEvent.ERROR, data={"error": str(e)}))
        return 255


def _wait_for_empty_queue() -> None:
    """Wait until the event queue is empty."""
    while get_queue_size() > 0:
        time.sleep(_SEARCHING_DELAY)
    time.sleep(_AFTER_READ_DELAY)


def write_openprinttag(reader: ExtendedISO15693Sensor, uid: str, data: bytes) -> bool:
    """Process a write command - wait for tag and write data.

    Args:

        reader: The RFID sensor instance.
        data: Raw bytes to write to the tag.

    Returns:
        True if write succeeded, False otherwise.
    """
    register_event(
        EventDto(
            event_type=TagReadEvent.SEARCHING_WRITE,
            data={"mode": "write", "bytes": len(data)},
        )
    )

    # Write data to tag
    # TODO: Implement working indication of successful write
    _ = reader.write_multi_blocks(data)

    # Invalidate cache if key exists
    _ = __in_cache(uid, force_delete=True)
    _, _main, _ = parse_openprinttag(data)
    register_event(
        EventDto(
            event_type=TagReadEvent.SUCCESS_WRITE,
            data={
                "tag_info": TagDto.model_construct(**_main.model_dump(), tag_uid=uid)
                if _main
                else None
            },
        )
    )
    # For now simple delay added.
    time.sleep(_AFTER_READ_DELAY)

    return True


def search_tag(
    reader: ExtendedISO15693Sensor,
    search_type: Literal[
        TagReadEvent.SEARCHING_READ, TagReadEvent.SEARCHING_WRITE
    ] = TagReadEvent.SEARCHING_READ,
    skip_cache: bool = False,
) -> str | None:
    """Iterating method waiting for a tag. Reads tag uid and returns.
    if uid in cache then CACHE_HIT event triggered (unless skip_cache=True).
    Uid is validated before method returns it and if not valid
    TAG_UID_INVALID event is registered.

    Args:
        reader: The RFID sensor instance.
        skip_cache: If True, ignore cache and return any valid tag (used for write mode).
    """

    _start_time = time.time()
    _uid: str | None = None
    _searching: bool = True
    while _searching:
        # Escape loop when new bin file detected
        # it returns True even if cancel message received,
        # so the searching loop is escaped.
        if has_openprinttag_bin():
            return None

        _uid = reader.read_tag()
        if not _uid:
            _start_time = __trigger_searching_event(_start_time, search_type)
            time.sleep(_SEARCHING_DELAY)
            continue
        if _invalid(_uid):
            register_event(
                EventDto(event_type=TagReadEvent.TAG_UID_INVALID, data={"uid": _uid})
            )
            time.sleep(_AFTER_READ_DELAY)
            continue
        if not skip_cache and __in_cache(_uid):
            time.sleep(_AFTER_READ_DELAY)
            continue
        _start_time = time.time()
        register_event(
            EventDto(event_type=TagReadEvent.TAG_DETECTED, data={"uid": _uid})
        )
        _searching = False
    return _uid


def __pn5180_thread(reader: ExtendedISO15693Sensor) -> None:
    """Thread for reading rfid tags. Also handles write operations from queue."""
    while True:
        try:
            # Check for pending write operations first
            # if cancel message received,
            # it will return None and continue to searching mode.
            _openprinttag_data: bytes | None = get_openprinttag_bin()

            # Write mode
            if _openprinttag_data:
                _uid = search_tag(
                    reader, search_type=TagReadEvent.SEARCHING_WRITE, skip_cache=True
                )
                if not _uid:
                    continue

                _filament_usage.cancel_not_processed_messages_for_tag(_uid)
                write_openprinttag(reader, _uid, _openprinttag_data)
                _wait_for_empty_queue()
                continue

            # Read mode - search for tags and read data
            _uid = search_tag(reader)
            # If _uid is None here, it means we got interrupted.
            # and should write data to first tag detected.
            if not _uid:
                continue

            _usage = _filament_usage.get_total_filament_usage_by_tag_uid_status(
                _uid, "NOT_PROCESSED"
            )
            if _usage:
                print(
                    f"Here we can save usage to the tag... UID: {_uid}, usage: {_usage}mm"
                )

            _main: OpenPrintTagMain | None = read_openprinttag(
                reader, get_number_blocks(reader)
            )
            if _main:
                __put_cache(_uid, _main)
                register_event(
                    EventDto(
                        event_type=TagReadEvent.SUCCESS_READ,
                        data={
                            "tag_info": TagDto.model_construct(
                                **_main.model_dump(), tag_uid=_uid
                            )
                        },
                    )
                )
            else:
                register_event(
                    EventDto(
                        event_type=TagReadEvent.ERROR,
                        data={"error": f"Empty or corrupted tag data for UID: {_uid}"},
                    )
                )
            _wait_for_empty_queue()
        except Exception as e:
            register_event(
                EventDto(
                    event_type=TagReadEvent.ERROR,
                    data={"error": f"Unhandled error in tag thread: {e}"},
                )
            )
            time.sleep(_AFTER_READ_DELAY)


def run(pi: pigpio.pi) -> None:
    """Start the PN5180 reader thread."""
    reader = ExtendedISO15693Sensor(pi)
    Thread(target=__pn5180_thread, args=(reader,), daemon=True).start()

    sensor_info = {"sensor": "PN5180", "protocol": "ISO15693", "status": "initialized"}
    register_event(EventDto(event_type=TagReadEvent.WELCOME, data=sensor_info))
