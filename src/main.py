import pigpio
import logging
from default.callbacks import register_default_callbacks
from default.openprinttag_reader import run as run_openprinttag_reader
from common.api import run as run_callbacks_thread

PIN_RST = 7
PIN_BUSY = 25

PIN_IRQ = 23
SPI_CHANNEL = 0
SPI_SPEED = 1_000_000

pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("pigpio daemon not running")

pi.set_mode(PIN_RST,  pigpio.OUTPUT)
pi.set_mode(PIN_BUSY, pigpio.INPUT)

logging.info("PigPio Initialization complete.")

if __name__ == "__main__":
    register_default_callbacks()
    run_callbacks_thread()
    run_openprinttag_reader(pi)






