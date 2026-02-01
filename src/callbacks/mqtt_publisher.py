"""Simple MQTT publisher for tag information."""

import logging
from typing import Optional
import paho.mqtt.client as mqtt

from models.openprinttag_main import OpenPrintTagMain
from models.event_dto import EventDto
from common.api import register_callback
from common.enum import TagReadEvent
from urllib.parse import urlencode


class MQTTPublisher:
    """Publishes tag information via MQTT."""

    def __init__(
        self, broker: str = "localhost", port: int = 1883, topic: str = "rfid/tag"
    ):
        """
        Initialize MQTT publisher.
        Broker is the MQTT broker address.
        Port is the MQTT broker port.
        Topic is the MQTT topic to publish tag information to.
        """
        self.topic = topic
        self.client = mqtt.Client()

        try:
            self.client.connect(broker, port, 60)
            self.client.loop_start()
            # print(f"MQTT connected to {broker}:{port}")
        except Exception:
            # print(f"MQTT connection failed: {e}")
            self.client = None

    def _publish_tag(self, tag: OpenPrintTagMain) -> None:
        """Publish tag information to MQTT topic in URL-encoded form data format with retain flag."""

        data = {
            "manufacturer": tag.manufacturer or "",
            "material": tag.material_name or "",
            "color": tag.primary_color_hex or "",
            "min_print_temp": tag.min_print_temperature or 0,
            "max_print_temp": tag.max_print_temperature or 0,
            "preheat_temp": tag.preheat_temperature or 0,
            "min_bed_temp": tag.min_bed_temperature or 0,
            "max_bed_temp": tag.max_bed_temperature or 0,
        }
        payload = urlencode(data)

        try:
            self.client.publish(self.topic, payload, retain=True)
        except Exception as e:
            logging.error(f"MQTT publish failed: {e}")

    def on_success(self, event: EventDto) -> None:
        """Callback for successful tag read."""
        tag_info: Optional[OpenPrintTagMain] = event.data.get("tag_info")
        if tag_info:
            self._publish_tag(tag_info)


def setup_mqtt_publisher(
    broker: str = "localhost", port: int = 1883, topic: str = "openprinttag"
):
    """Setup MQTT publisher and register callbacks."""
    _publisher = MQTTPublisher(broker, port, topic)
    if _publisher.client:
        register_callback(TagReadEvent.SUCCESS, _publisher.on_success)
