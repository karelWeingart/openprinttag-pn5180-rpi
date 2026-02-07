""" mainly for the callbacks -
sensor thread is started in openprinttag.reader.run
and all callbacks are inited here - so make your main.py
and register your callbacks..
"""
import pigpio
import time
from callbacks.console import register_default_callbacks
from callbacks.led_neopixel import register_neopixel_callbacks
from callbacks.mqtt_publisher import setup_mqtt_publisher
from openprinttag.reader import run as run_openprinttag_reader
from common.api import run as run_callbacks_thread

PIN_RST = 7
PIN_BUSY = 25

PIN_IRQ = 23
SPI_CHANNEL = 0
SPI_SPEED = 1_000_000

if __name__ == "__main__":
    pi = pigpio.pi()
    if not pi.connected:
        raise RuntimeError("pigpio daemon not running")

    pi.set_mode(PIN_RST, pigpio.OUTPUT)
    pi.set_mode(PIN_BUSY, pigpio.INPUT)

    # logging.info("Pigpio initialization complete.")

    register_default_callbacks()
    register_neopixel_callbacks()
    setup_mqtt_publisher()
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
