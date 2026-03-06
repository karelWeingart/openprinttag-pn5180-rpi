"""MQTT publisher for bin files.
bin files generated at the openprinttag.org portal 
are published to the MQTT topic "openprinttag/pn5180/bin" for consumption by the pn5180 reader.
"""

import logging

from openprinttag_shared.common_mqtt.publisher import MQTTPublisher
from openprinttag_shared.common_mqtt.config import ( 
    MQTT_BROKER, MQTT_PORT, MQTT_WRITE_QUEUE_TOPIC_NAME
) 

_bin_file_publisher: MQTTPublisher  = MQTTPublisher.get_instance(MQTT_BROKER, MQTT_PORT)


def publish_openprinttag_data(data: str | bytes) -> bool:
    """Publish a bin file to the MQTT topic for the pn5180 reader.

    Args:
        data: The data to publish."""
    try:
        _bin_file_publisher.publish(MQTT_WRITE_QUEUE_TOPIC_NAME, data)
        logging.info(f"Published bin file to MQTT topic: {MQTT_WRITE_QUEUE_TOPIC_NAME}")
        return True
    except Exception as e:
        logging.error("Failed to publish bin file to MQTT: %s", e)
        return False
    