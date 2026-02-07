""" Simple module to handle openprinttag-pn5180 events for neopixel led """
import board
from common.api import register_callback, TagReadEvent
from models.event_dto import EventDto
import time
import neopixel

""" Default setup. 
TODO: parametrize this.
"""
pixels = neopixel.NeoPixel(
    board.D18, 1, brightness=0.2, auto_write=True, pixel_order=neopixel.GRB
)

_PRUSA_ORANGE: tuple[int, int, int] = (80, 253, 0)
_PRUSA_ORANGE_COMPLEMENTARY: tuple[int, int, int] = (175, 2, 255)
_ALERT_COLOR: tuple[int, int, int] = (5, 64, 0)
_SUCCESS_COLOR: tuple[int, int, int] = tuple(
    int(c / 4) for c in _PRUSA_ORANGE_COMPLEMENTARY
)

def _blink(
    color: tuple[int, int, int],
    number_of_blinks: int = 1,
    length_of_blink: float = 0.2,
) -> None:
    """Blink the LED with the specified color, number of times, and duration.  
    Speeds the blink in iterations.
    """
    for i in range(number_of_blinks):
        pixels[0] = color
        time.sleep(length_of_blink)
        pixels[0] = (0, 0, 0)
        time.sleep(length_of_blink/i if i else length_of_blink)


def _fade_out(
    start_color: tuple[int, int, int], steps: int = 20, delay: float = 0.05
) -> None:
    """ Fade out - steps * delay is total time. Always ends in [0,0,0]"""
    r, g, b = start_color
    for i in range(steps):
        factor = (steps - i) / steps
        pixels[0] = (int(r * factor), int(g * factor), int(b * factor))
        time.sleep(delay)
    pixels[0] = (0, 0, 0)

def _on_cache_hit(_event: EventDto) -> None:
    """Flash the LED quickly to indicate a cache hit."""
    _color  = tuple(int(c / 5) for c in _SUCCESS_COLOR)
    _blink(_color, number_of_blinks=5, length_of_blink=0.05)

def _on_tag_uid_invalid(_event: EventDto) -> None:
    """Flash the LED in alert color to indicate an invalid tag UID."""
    _blink(_ALERT_COLOR, number_of_blinks=5, length_of_blink=0.05)

def _on_welcome(_event: EventDto) -> None:
    """ on_welcome led callback. """
    start = _PRUSA_ORANGE_COMPLEMENTARY
    target = _PRUSA_ORANGE
    steps = 40
    delay = 1.0 / steps
    sr, sg, sb = start
    tr, tg, tb = target
    for i in range(steps):
        t = (i + 1) / steps
        r = int(sr + (tr - sr) * t)
        g = int(sg + (tg - sg) * t)
        b = int(sb + (tb - sb) * t)
        pixels[0] = (r, g, b)
        time.sleep(delay)
    pixels[0] = target
    _fade_out(target, steps=20, delay=0.05)


def _on_tag_detected(_event: EventDto) -> None:
    """ TagReadEvent.TAG_DETECTED callback. """
    _fade_out(tuple(int(c / 10) for c in _PRUSA_ORANGE_COMPLEMENTARY), steps=5, delay=0.03)


def _on_error(_event: EventDto) -> None:
    """ TagReadEvent.ERROR callback. """
    _fade_out(_ALERT_COLOR, steps=20, delay=0.05)


def _on_success(_event: EventDto) -> None:
    """" TagReadEvent.SUCCESS callback. """
    _fade_out(_SUCCESS_COLOR, steps=20, delay=0.05)


def _on_block_uploaded(_event: EventDto) -> None:
    """ TagReadEvent.BLOCK_UPLOADED callback. """
    _faded_color = tuple(int(c / 20) for c in _PRUSA_ORANGE_COMPLEMENTARY)
    _block = _event.data.get("block", 0)
    _blocks = _event.data.get("blocks", 1)
    _percent = (_block / _blocks) if _blocks else 0
    _fade_out(tuple(int(c * _percent) for c in _faded_color), steps=5, delay=0.03)


def _on_searching(_event: EventDto) -> None:
    """ TagReadEvent.SEARCHING  callback. """
    _fade_out(
        tuple(int(c / 30) for c in _PRUSA_ORANGE), steps=5, delay=0.01
    )


def register_neopixel_callbacks() -> None:
    """Register NeoPixel LED callbacks for RFID events."""
    register_callback(TagReadEvent.TAG_DETECTED, _on_tag_detected)
    register_callback(TagReadEvent.ERROR, _on_error)
    register_callback(TagReadEvent.SUCCESS, _on_success)
    register_callback(TagReadEvent.BLOCK_UPLOADED, _on_block_uploaded)
    register_callback(TagReadEvent.SEARCHING, _on_searching)
    register_callback(TagReadEvent.WELCOME, _on_welcome)
    register_callback(TagReadEvent.CACHE_HIT, _on_cache_hit)
    register_callback(TagReadEvent.TAG_UID_INVALID, _on_tag_uid_invalid)
