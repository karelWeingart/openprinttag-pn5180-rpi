import board
from common.api import register_callback, TagReadEvent
from models.event_dto import EventDto
import time
import neopixel

pixels = neopixel.NeoPixel(
    board.D18, 1, brightness=0.2, auto_write=True, pixel_order=neopixel.GRB
)

_PRUSA_ORANGE: tuple[int, int, int] = (80, 253, 0)
_PRUSA_ORANGE_COMPLEMENTARY: tuple[int, int, int] = (175, 2, 255)
_ALERT_COLOR: tuple[int, int, int] = (5, 64, 0)
_SUCCESS_COLOR: tuple[int, int, int] = tuple(
    int(c / 4) for c in _PRUSA_ORANGE_COMPLEMENTARY
)

_LED_POINTER = pixels[0]


def _fade_out(
    start_color: tuple[int, int, int], steps: int = 20, delay: float = 0.05
) -> None:
    r, g, b = start_color
    for i in range(steps):
        factor = (steps - i) / steps
        pixels[0] = (int(r * factor), int(g * factor), int(b * factor))
        time.sleep(delay)
    pixels[0] = (0, 0, 0)


def _on_welcome(_event: EventDto) -> None:
    _fade_out(_PRUSA_ORANGE, steps=20, delay=0.1)


def _on_tag_detected(_event: EventDto) -> None:
    _fade_out(tuple(int(c / 10) for c in _PRUSA_ORANGE), steps=5, delay=0.03)


def _on_error(_event: EventDto) -> None:
    _fade_out(_ALERT_COLOR, steps=20, delay=0.05)


def _on_success(_event: EventDto) -> None:
    _fade_out(_SUCCESS_COLOR, steps=20, delay=0.05)


def _on_block_uploaded(_event: EventDto) -> None:
    _faded_color = tuple(int(c / 20) for c in _PRUSA_ORANGE_COMPLEMENTARY)
    _block = _event.data.get("block", 0)
    _blocks = _event.data.get("blocks", 1)
    _percent = (_block / _blocks) if _blocks else 0
    _fade_out(tuple(int(c * _percent) for c in _faded_color), steps=5, delay=0.03)


def _on_searching(_event: EventDto) -> None:
    _fade_out(
        tuple(int(c / 10) for c in _PRUSA_ORANGE_COMPLEMENTARY), steps=6, delay=0.02
    )


def register_neopixel_callbacks() -> None:
    """Register NeoPixel LED callbacks for RFID events."""
    register_callback(TagReadEvent.TAG_DETECTED, _on_tag_detected)
    register_callback(TagReadEvent.ERROR, _on_error)
    register_callback(TagReadEvent.SUCCESS, _on_success)
    register_callback(TagReadEvent.BLOCK_UPLOADED, _on_block_uploaded)
    register_callback(TagReadEvent.SEARCHING, _on_searching)
    register_callback(TagReadEvent.WELCOME, _on_welcome)
