"""Write queue for receiving bin files via MQTT to write to tags."""

from queue import Queue, Empty
import logging

# from openprinttag-shared package
from openprinttag_shared.common_mqtt.subscriber import MQTTSubscriber

# Thread-safe write queue for incoming MQTT write commands
_write_queue: Queue[bytes] = Queue(1)
_subscriber: MQTTSubscriber | None = None


def _on_write_data(payload: bytes) -> None:
    """Callback for write queue messages."""
    if payload:
        _write_queue.put(payload)
        logging.info("OpenPrintTag bin file detected in queue: %d bytes", len(payload))


def setup_write_queue(broker, port: int, topic: str) -> bool:
    """Setup MQTT subscriber for the write queue.

    Args:
        broker: MQTT broker address.
        port: MQTT broker port.
        topic: MQTT topic to subscribe for write commands.

    Returns:
        True if setup succeeded, False otherwise.
    """
    global _subscriber  # pylint: disable=global-statement

    _subscriber = MQTTSubscriber(broker, port)
    _subscriber.subscribe(topic, _on_write_data)

    if _subscriber.connect():
        logging.info("Write queue listening on: %s", topic)
        return True

    _subscriber = None
    return False


def get_openprinttag_bin() -> bytes | None:
    """Get pending write data from queue if available (thread-safe).

    Returns:
        Write data bytes or None if queue is empty.
        It returns None if "cancel" message is received.
    """
    try:
        _data = _write_queue.get_nowait()
        if _data == b"cancel":
            return None
        return _data
    except Empty:
        return None


def has_openprinttag_bin() -> bool:
    """Check if there's pending write data without consuming it.

    Returns:
        True if there's pending data, False otherwise.
    """
    return not _write_queue.empty()
