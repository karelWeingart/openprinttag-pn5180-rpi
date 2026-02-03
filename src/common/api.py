from threading import Thread
from queue import Queue
from common.enum import TagReadEvent, TagReadEventType
from typing import Callable
import logging

from models.event_dto import EventDto

# Event queue
_event_queue = Queue(1000)

_callbacks: dict[TagReadEventType, list[Callable]] = {}


# register_callback
def register_callback(event: TagReadEventType, callback: Callable) -> None:
    """Register a callback for a specific TagReadEventType.
    More callbacks can be registered for the same event.
    Order of execution is the order of registration.
    """
    if event not in _callbacks:
        _callbacks[event] = []
    _callbacks[event].append(callback)


def register_event(event: EventDto) -> None:
    """Register an event to be processed by the callbacks thread."""
    _event_queue.put(event)


def __get_event_type_from_event(event: EventDto) -> TagReadEventType:
    if isinstance(event.event_type, TagReadEvent):
        return event.event_type
    raise ValueError("Unknown event type")


def __run_callbacks_for_event(event: EventDto) -> None:
    event_type = __get_event_type_from_event(event)
    if event_type in _callbacks:
        for callback in _callbacks[event_type]:
            callback(event)

def __callbacks_thread():
    while True:
        if not _event_queue.empty():
            __run_callbacks_for_event(_event_queue.get())

def get_queue_size() -> int:
    """Get the current size of the event queue."""
    return _event_queue.qsize()

def run() -> None:
    """Start the callbacks thread."""
    logging.info("Starting callbacks thread...")
    Thread(target=__callbacks_thread, daemon=True).start()
