from threading import Thread
from extended_sensor import ExtendedISO15693Sensor
from models.event_dto import EventDto
from openprinttag_parser import parse_openprinttag
import pigpio
import time
import logging
from common.api import TagReadEvent, register_event

def __read_openprinttag(reader, num_blocks: int):
    """ Read OpenPrintTag data from the tag using the provided reader."""
    _data = reader.read_multi_blocks(num_blocks)
    return parse_openprinttag(_data)

def __pn5180_thread(pi: pigpio.pi) -> None:
    
    reader = ExtendedISO15693Sensor(pi)
    while True:
        _uid = reader.read_tag()
        if not _uid:
            time.sleep(0.2)
            continue
            
        register_event(EventDto(event_type=TagReadEvent.TAG_DETECTED, data={"uid": _uid}))
        _info=reader.get_system_info()
        _info_dict = reader.parse_system_info(_info)
        meta, main, aux = __read_openprinttag(reader, _info_dict.get("num_blocks", 256))

        print("Meta:", meta)
        print("Main:", main)
        print("Aux:", aux)

        time.sleep(0.1)

def run(pi:pigpio.pi) -> None:
    """ Start the PN5180 reader thread. """

    logging.info("Starting PN5180 reader thread...")
    
    Thread(target=__pn5180_thread, args=(pi,), daemon=True).start()