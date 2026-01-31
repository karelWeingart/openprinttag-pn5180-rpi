from common.api import register_callback
from common.enum import TagReadEvent
from models.event_dto import EventDto

def __on_tag_detected(event: EventDto) -> None:
    print(f"Tag detected with UID: {event.data.get('uid')}", end="\r")

def register_default_callbacks() -> None:
    """ Register default callbacks for RFID events. """   
    register_callback(TagReadEvent.TAG_DETECTED, __on_tag_detected)