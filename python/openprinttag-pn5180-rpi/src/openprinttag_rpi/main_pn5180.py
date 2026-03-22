"""mainly for the callbacks -
sensor thread is started in openprinttag.reader.run
and all callbacks are inited here - so make your main.py
and register your callbacks..
"""

import pigpio  # type: ignore[import-untyped]
import time
from openprinttag_rpi.callbacks.console import register_default_callbacks
from openprinttag_rpi.callbacks.led_neopixel import register_neopixel_callbacks
from openprinttag_rpi.callbacks.mqtt_publisher import setup_mqtt_publisher
from openprinttag_rpi.callbacks.webapi_publisher import setup_webapi_publisher
from openprinttag_rpi.mqtt.tag_write_queue import setup_write_queue
from openprinttag_rpi.openprinttag.reader import run as run_openprinttag_reader
from openprinttag_rpi.common.api import run as run_callbacks_thread
from openprinttag_shared.common_mqtt.config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_WRITE_QUEUE_TOPIC_NAME,
)
from openprinttag_rpi.database import init_db

PIN_RST = 7
PIN_BUSY = 25

PIN_IRQ = 23
SPI_CHANNEL = 0
SPI_SPEED = 1_000_000


def __main__():
    """Main entry point for OpenPrintTag application."""
    pi = pigpio.pi()
    if not pi.connected:
        raise RuntimeError("pigpio daemon not running")

    pi.set_mode(PIN_RST, pigpio.OUTPUT)
    pi.set_mode(PIN_BUSY, pigpio.INPUT)

    init_db()

    # logging.info("Pigpio initialization complete.")

    register_default_callbacks()
    register_neopixel_callbacks()
    setup_mqtt_publisher()
    setup_webapi_publisher()
    setup_write_queue(
        broker=MQTT_BROKER, port=MQTT_PORT, topic=MQTT_WRITE_QUEUE_TOPIC_NAME
    )
    run_callbacks_thread()
    run_openprinttag_reader(pi)
    _stopped = False
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # logging.info("Shutting down...")
        _stopped = True
    finally:
        pi.stop()
        if _stopped:
            exit(0)


if __name__ == "__main__":
    __main__()
