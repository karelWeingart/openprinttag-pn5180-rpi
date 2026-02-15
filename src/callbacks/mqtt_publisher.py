"""Simple MQTT publisher for tag information."""

import logging
from typing import Optional
import paho.mqtt.client as mqtt

from models.openprinttag_main import OpenPrintTagMain
from models.event_dto import EventDto
from common.api import register_callback
from common.enum import TagReadEvent


class MQTTPublisher:
    """Publishes tag information via MQTT."""

    def __init__(
        self, 
        broker: str = "localhost",
        port: int = 1883, 
        topic: str = "rfid/tag"
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
        except Exception:
            self.client = None

    def _publish_tag(self, tag: OpenPrintTagMain) -> None:
        """Publish tag information to MQTT topic in URL-encoded form data format with retain flag.
        TODO: custom list of fields to be published.
        """

        data = {
                "Material": tag.material_name or tag.material_abbreviation,
                "Manufacturer": tag.manufacturer or 'Unknown',
                "Color": tag.primary_color_hex or "",
                "Max/Min Temp": f"{tag.min_print_temperature or '-'}/{tag.max_print_temperature or '-'}",
            }

        try:
            _body = "&".join(f"{k}={'' if v is None else str(v)}" for k, v in data.items())
            _ = self.client.publish(self.topic, _body, retain=True)
        except Exception as e:
            logging.error(f"MQTT publish failed: {e}")

    def on_success(self, event: EventDto) -> None:
        """Callback for successful tag read."""
        tag_info: Optional[OpenPrintTagMain] = event.data.get("tag_info")
        if tag_info:
            self._publish_tag(tag_info)


def setup_mqtt_publisher(
    broker: str = "localhost", port: int = 1883, topic: str = "rfid/tag"
):
    """Setup MQTT publisher and register callbacks."""
    _publisher = MQTTPublisher(broker, port, topic)
    if _publisher.client:
        register_callback(TagReadEvent.SUCCESS, _publisher.on_success)
