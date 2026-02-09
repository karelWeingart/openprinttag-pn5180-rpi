""" reader module - that initializes sensor and reading thread
S"""
from threading import Thread
from pn5180_rpi.sensor import (
    ExtendedISO15693Sensor,
    CommandError,
    PostCommandError,
    PreCommandError,
)
from models.event_dto import EventDto
from openprinttag.parser import parse_openprinttag, parse_system_info
import pigpio
import time
from common.api import TagReadEvent, get_queue_size, register_event
from models.openprinttag_main import OpenPrintTagMain

_SEARCHING_DELAY = 0.1
_SEARCHING_EVENT_INTERVAL = 5.0
_AFTER_READ_DELAY = 2

_TAG_CACHE_: dict[str, tuple[OpenPrintTagMain, float]] = {}
_TAG_CACHE_TTL: float = 120.0  # seconds


def __read_openprinttag(reader: ExtendedISO15693Sensor, num_blocks: int) -> OpenPrintTagMain:
    """Reads OpenPrintTag data from the tag using the provided reader."""
    try:
        _data = reader.read_multi_blocks(num_blocks)
        return parse_openprinttag(_data)[1]
    except (CommandError, PreCommandError, PostCommandError, ValueError) as e:
        register_event(EventDto(event_type=TagReadEvent.ERROR, data={"error": str(e)}))
        return None


def __trigger_searching_event(start_time: float) -> float:
    """Trigger SEARCHING event at defined intervals."""
    current_time = time.time()
    if current_time - start_time >= _SEARCHING_EVENT_INTERVAL:
        register_event(EventDto(event_type=TagReadEvent.SEARCHING))
        return current_time
    return start_time


def _invalid(uid: str) -> bool:
    """Check if the UID is invalid. """   
   
    if len(uid) < 16:
        return True
  
    if len(set(uid)) == 1:
        return True
    
    return False

def __put_cache(uid: str, tag_info: OpenPrintTagMain) -> None:
    """Put the UID and tag info into the recent cache."""
    _TAG_CACHE_[uid] = (tag_info, time.time())

def __in_cache(uid: str) -> bool:
    """Check if the UID is in the recent cache to avoid duplicate reads."""
    if uid in _TAG_CACHE_:
        cached_time = _TAG_CACHE_[uid][1]
        cached_data = _TAG_CACHE_[uid][0]
        if time.time() - cached_time < _TAG_CACHE_TTL:
            register_event(
                EventDto(event_type=TagReadEvent.CACHE_HIT, data={"tag_info": cached_data})
            )
            return True
        else:
            del _TAG_CACHE_[uid]  # Remove stale cache entry
    return False

def _get_number_blocks(reader: ExtendedISO15693Sensor) -> int:
    """Retrieve and parse system information from the tag.
    For now not blocking on errors to allow further reading attempts.
    """
    try:
        _info = reader.get_system_info()
        _info_dict = parse_system_info(_info)
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

def _search_tag(reader: ExtendedISO15693Sensor) -> str | None:
    """ Iterating method waiting for a tag. Reads tag uid and returns.
    if uid in cache then CACHE_HIT event triggered.
    Uid is validated before method returns it and if not valid
    TAG_UID_INVALID event is registered.
    """
    
    _start_time = time.time()
    _uid: str | None = None
    _searching: bool = True
    while _searching:
        _uid = reader.read_tag()
        if not _uid:
            _start_time = __trigger_searching_event(_start_time)
            time.sleep(_SEARCHING_DELAY)
            continue
        if _invalid(_uid):
            register_event(EventDto(event_type=TagReadEvent.TAG_UID_INVALID, data={"uid": _uid}))
            time.sleep(_AFTER_READ_DELAY)
            continue
        if __in_cache(_uid):
            time.sleep(_AFTER_READ_DELAY)
            continue
        _start_time = time.time()
        register_event(
            EventDto(event_type=TagReadEvent.TAG_DETECTED, data={"uid": _uid})
        )
        _searching = False
    print(_uid)
    return _uid


def __tag_reader_thread(reader: ExtendedISO15693Sensor) -> None:
    """ Thread for reading rfid tags. """
    while True:
        _uid: str = _search_tag(reader)

        _main: OpenPrintTagMain | None = __read_openprinttag(
            reader, _get_number_blocks(reader)
        )
        if _main:
            __put_cache(_uid, _main)
            register_event(
                EventDto(event_type=TagReadEvent.SUCCESS, data={"tag_info": _main})
            )
        else:
            register_event(EventDto(event_type=TagReadEvent.ERROR, 
                                    data={"error": f"Empty or corrupted tag data for UID: {_uid}"}))
        _wait_for_empty_queue()

def run(pi: pigpio.pi) -> None:
    """Start the PN5180 reader thread."""
    reader = ExtendedISO15693Sensor(pi)
    Thread(target=__tag_reader_thread, args=(reader,), daemon=True).start()

    sensor_info = {"sensor": "PN5180", "protocol": "ISO15693", "status": "initialized"}
    register_event(EventDto(event_type=TagReadEvent.WELCOME, data=sensor_info))
