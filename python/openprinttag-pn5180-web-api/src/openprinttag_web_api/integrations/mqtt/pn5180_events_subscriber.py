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

    if event_type not in {"success_read", "success_write", "error"}:
        logging.warning(f" MQTT event type: {event_type}")
        return

    tag = event_message.tag
    tag_uid: str | None = tag.tag_uid if tag else None
    success = 0 if event_type == "error" else 1

    try:
        with get_db() as db:
            tag_id: int | None = None

            # Insert tag if tag info is present (dedup by uid + data)
            if tag:
                tag_data = tag.model_dump_json()
                db.execute(
                    """
                    INSERT OR IGNORE INTO tags (tag_uid, data)
                    VALUES (?, ?)
                    """,
                    (tag_uid, tag_data),
                )
                row = db.execute(
                    "SELECT id FROM tags WHERE tag_uid = ? AND data = ?",
                    (tag_uid, tag_data),
                ).fetchone()
                tag_id = row[0] if row else None

            # Insert event
            db.execute(
                "INSERT INTO events (event_type, tag_id, success) VALUES (?, ?, ?)",
                (event_type, tag_id, success),
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
