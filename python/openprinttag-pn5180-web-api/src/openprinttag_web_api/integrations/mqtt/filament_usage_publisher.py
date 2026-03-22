"""MQTT publisher for bin files.
bin files generated at the openprinttag.org portal
are published to the MQTT topic "openprinttag/pn5180/bin" for consumption by the pn5180 reader.
"""

import logging
from openprinttag_shared.common_mqtt.models import FilamentUsageDto
from openprinttag_shared.models.dto import CompletedJobDto
from openprinttag_shared.common_mqtt.publisher import MQTTPublisher
from openprinttag_shared.common_mqtt.config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_FILAMENT_USAGE_TOPIC_NAME,
)

_filament_usage_publisher: MQTTPublisher = MQTTPublisher.get_instance(
    MQTT_BROKER, MQTT_PORT
)


def publish_filament_usage_data(data: CompletedJobDto, tag_uid: str) -> bool:
    """Publish a bin file to the MQTT topic for the pn5180 reader.

    Args:
        data: The data to publish."""
    try:
        _dto = FilamentUsageDto(tag_uid=tag_uid, job_data=data)
        _filament_usage_publisher.publish(
            MQTT_FILAMENT_USAGE_TOPIC_NAME, _dto.model_dump_json()
        )
        logging.info(
            "Published filament usage data to MQTT topic: %s",
            MQTT_FILAMENT_USAGE_TOPIC_NAME,
        )
        return True
    except Exception as e:
        logging.error("Failed to publish bin file to MQTT: %s", e)
        return False
