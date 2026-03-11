"""Simple MQTT publisher for tag information."""

from openprinttag_shared.common_mqtt.publisher import MQTTPublisher
from openprinttag_shared.common_mqtt.config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_WEB_API_TOPIC_NAME,
)
from openprinttag_shared.common_mqtt.models import EventMessage
from openprinttag_rpi.models.event_dto import EventDto
from openprinttag_shared.models.dto import ErrorDto
from openprinttag_rpi.common.api import register_callback
from openprinttag_rpi.common.enum import TagReadEvent, TagReadEventType


_publisher = MQTTPublisher.get_instance(MQTT_BROKER, MQTT_PORT)


def _publish_event(event: EventDto, event_type: TagReadEventType) -> None:
    """Publish event information to MQTT topic in JSON format with retain flag."""
    if event.data and (tag_info := event.data.get("tag_info")):
        _event_message = EventMessage(
            event_type=event_type.value,
            tag=tag_info,
            error=None,
        )
        _publisher.publish(
            MQTT_WEB_API_TOPIC_NAME, _event_message.model_dump_json(), retain=False
        )


def _on_success_read(event: EventDto) -> None:
    """Callback for successful tag read."""
    _publish_event(event, TagReadEvent.SUCCESS_READ)


def _on_success_write(event: EventDto) -> None:
    """Callback for successful tag write."""
    _publish_event(event, TagReadEvent.SUCCESS_WRITE)


def _on_error(event: EventDto) -> None:
    """Callback for tag read/write error."""
    error_message = event.data.get("error", "") if event.data else "Unknown error"
    _event_message = EventMessage(
        event_type=TagReadEvent.ERROR.value, error=ErrorDto(error=error_message)
    )
    _publisher.publish(
        MQTT_WEB_API_TOPIC_NAME, _event_message.model_dump_json(), retain=False
    )


def _on_searching_read(_: EventDto) -> None:
    """Callback for tag searching read event."""
    _event_message = EventMessage(event_type=TagReadEvent.SEARCHING_READ.value)
    _publisher.publish(
        MQTT_WEB_API_TOPIC_NAME, _event_message.model_dump_json(), retain=False
    )


def _on_searching_write(_: EventDto) -> None:
    """Callback for tag searching write event."""
    _event_message = EventMessage(event_type=TagReadEvent.SEARCHING_WRITE.value)
    _publisher.publish(
        MQTT_WEB_API_TOPIC_NAME, _event_message.model_dump_json(), retain=False
    )


def setup_webapi_publisher() -> None:
    """Setup MQTT publisher and register callbacks."""
    if _publisher.connect():
        register_callback(TagReadEvent.SUCCESS_READ, _on_success_read)
        register_callback(TagReadEvent.SUCCESS_WRITE, _on_success_write)
        register_callback(TagReadEvent.ERROR, _on_error)
        register_callback(TagReadEvent.SEARCHING_READ, _on_searching_read)
        register_callback(TagReadEvent.SEARCHING_WRITE, _on_searching_write)
