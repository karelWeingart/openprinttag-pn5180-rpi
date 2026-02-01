from threading import Thread
from pn5180_rpi.sensor import (
    ExtendedISO15693Sensor,
    CommandError,
    PostCommandError,
    PreCommandError,
)
from models.event_dto import EventDto
from openprinttag.parser import parse_openprinttag
import pigpio
import time
from common.api import TagReadEvent, register_event
from models.openprinttag_main import OpenPrintTagMain

_WAIT_AFTER_SUCCESS = 2.0  # seconds
_SEARCHING_DELAY = 0.2  # seconds
_SEARCHING_EVENT_INTERVAL = 5.0  # seconds


def __read_openprinttag(reader, num_blocks: int) -> OpenPrintTagMain:
    """Read OpenPrintTag data from the tag using the provided reader."""
    try:
        _data = reader.read_multi_blocks(num_blocks)
        return parse_openprinttag(_data)[1]
    except (CommandError, PreCommandError, PostCommandError) as e:
        register_event(EventDto(event_type=TagReadEvent.ERROR, data={"error": str(e)}))
        return None


def __trigger_searching_event(start_time: float) -> float:
    """Trigger SEARCHING event at defined intervals."""
    current_time = time.time()
    if current_time - start_time >= _SEARCHING_EVENT_INTERVAL:
        register_event(EventDto(event_type=TagReadEvent.SEARCHING))
        return current_time
    return start_time


def __pn5180_thread(reader: ExtendedISO15693Sensor) -> None:
    _start_time: float = time.time()

    while True:
        _uid = reader.read_tag()

        if not _uid:
            _start_time = __trigger_searching_event(_start_time)
            time.sleep(_SEARCHING_DELAY)
            continue
        _start_time = time.time()
        register_event(
            EventDto(event_type=TagReadEvent.TAG_DETECTED, data={"uid": _uid})
        )
        _info = reader.get_system_info()
        _info_dict = reader.parse_system_info(_info)
        _main: OpenPrintTagMain | None = __read_openprinttag(
            reader, _info_dict.get("num_blocks", 256)
        )
        if _main:
            register_event(
                EventDto(event_type=TagReadEvent.SUCCESS, data={"tag_info": _main})
            )
            time.sleep(_WAIT_AFTER_SUCCESS)
        else:
            time.sleep(0.1)


def run(pi: pigpio.pi) -> None:
    """Start the PN5180 reader thread."""
    reader = ExtendedISO15693Sensor(pi)
    Thread(target=__pn5180_thread, args=(reader,), daemon=True).start()

    # Send welcome event with sensor info
    sensor_info = {"sensor": "PN5180", "protocol": "ISO15693", "status": "initialized"}
    register_event(EventDto(event_type=TagReadEvent.WELCOME, data=sensor_info))
