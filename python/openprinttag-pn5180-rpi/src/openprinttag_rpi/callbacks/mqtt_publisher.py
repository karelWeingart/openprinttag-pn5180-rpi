"""Simple MQTT publisher for tag information."""

import logging

from openprinttag_shared.common_mqtt.publisher import MQTTPublisher
from openprinttag_shared.common_mqtt.config import MQTT_BROKER, MQTT_PORT, MQTT_RFID_TAG_TOPIC_NAME
from openprinttag_rpi.models.openprinttag_main import OpenPrintTagMain
from openprinttag_rpi.models.event_dto import EventDto
from openprinttag_rpi.common.api import register_callback
from openprinttag_rpi.common.enum import TagReadEvent


_publisher = MQTTPublisher.get_instance(MQTT_BROKER, MQTT_PORT)

def _publish_tag(tag: OpenPrintTagMain) -> None:
    """Publish tag information to MQTT topic in URL-encoded form data format with retain flag.
    TODO: custom list of fields to be published.
    """

    data = {
        "Material": tag.material_name or tag.material_abbreviation,
        "Manufacturer": tag.manufacturer or "Unknown",
        "Color": tag.get_human_readable_color()
        or tag.primary_color_hex
        or "Unknown",
        "Max/Min Temp": f"{tag.min_print_temperature or '-'}/{tag.max_print_temperature or '-'}",
    }

    try:
        # Creating form-data like string from the dict for simpler parsing
        # on the esp32 consumer side.
        _body = "&".join(
            f"{k}={'' if v is None else str(v)}" for k, v in data.items()
        )
        _publisher.publish(MQTT_RFID_TAG_TOPIC_NAME, _body, retain=True)
    except Exception as e:
        logging.error("MQTT publish failed: %s", e)


def _on_success(event: EventDto) -> None:
    """Callback for successful tag read."""
    if event.data and (tag_info := event.data.get("tag_info")):
        _publish_tag(tag_info)


def setup_mqtt_publisher() -> None:
    """Setup MQTT publisher and register callbacks."""
    if _publisher.connect():
        register_callback(TagReadEvent.SUCCESS_READ, _on_success)
