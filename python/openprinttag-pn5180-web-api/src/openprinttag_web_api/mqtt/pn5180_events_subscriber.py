"""MQTT subscriber for pn5180 events — stores incoming events in the database."""

import json
import logging

from openprinttag_shared.common_mqtt.subscriber import MQTTSubscriber
from openprinttag_shared.common_mqtt.models import EventMessage
from openprinttag_shared.common_mqtt.config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_WEB_API_TOPIC_NAME,
)

from openprinttag_web_api.database import get_db

_subscriber: MQTTSubscriber | None = None


def _on_event(payload: bytes) -> None:
    """Handle an incoming event message from the pn5180 reader."""
    try:
        data = json.loads(payload)
        event_message = EventMessage(**data)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logging.error(f"Invalid MQTT event payload: {e}")
        return

    event_type = event_message.event_type
    if not event_type:
        logging.warning("MQTT event missing event_type, skipping")
        return
    
    if event_type not in {"success_read",  "success_write", "error"}:
        logging.warning(f" MQTT event type: {event_type}")
        return

    tag_uid: str | None = event_message.tag_uid
    success = 0 if event_type == "error" else 1

    try:
        with get_db() as db:
            # Upsert tag if tag info is present
            if tag_uid:
                db.execute(
                    """
                    INSERT INTO tags (tag_uid, material_type, manufacturer, name, color)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(tag_uid) DO UPDATE SET
                        material_type   = excluded.material_type,
                        manufacturer = excluded.manufacturer,
                        name      = excluded.name,
                        color      = excluded.color
                    """,
                    (
                        tag_uid,
                        event_message.material_type,
                        event_message.manufacturer,
                        event_message.name,
                        event_message.color,
                    ),
                )

            # Insert event
            db.execute(
                "INSERT INTO events (event_type, tag_uid, success) VALUES (?, ?, ?)",
                (event_type, tag_uid, success),
            )
            db.commit()

        logging.debug(f"Stored MQTT event: {event_type} (tag={tag_uid})")
    except Exception as e:
        logging.error(f"Failed to store MQTT event: {e}")


def start_subscriber(
    broker: str = MQTT_BROKER,
    port: int = MQTT_PORT,
    topic: str = MQTT_WEB_API_TOPIC_NAME,
) -> bool:
    """Connect to MQTT broker and start listening for pn5180 events.

    Returns:
        True if the subscriber connected successfully.
    """
    global _subscriber  # pylint: disable=global-statement

    _subscriber = MQTTSubscriber(broker, port)
    _subscriber.subscribe(topic, _on_event)

    if _subscriber.connect():
        logging.info(f"MQTT event subscriber listening on: {topic}")
        return True

    logging.error("Failed to start MQTT event subscriber")
    _subscriber = None
    return False


def stop_subscriber() -> None:
    """Disconnect the MQTT subscriber."""
    global _subscriber  # pylint: disable=global-statement
    if _subscriber:
        _subscriber.disconnect()
        _subscriber = None
