import logging
import json

from pydantic import ValidationError

from openprinttag_shared.common_mqtt.subscriber import MQTTSubscriber
from openprinttag_shared.common_mqtt.models import FilamentUsageDto

from openprinttag_rpi.repository.sqlite.filament_usage_message import SqliteFilamentUsageMessageRepository
from openprinttag_shared.models.dto import CompletedJobDto

_subscriber: MQTTSubscriber | None = None
_filament_usage_repository: SqliteFilamentUsageMessageRepository = SqliteFilamentUsageMessageRepository()

def _save_filament_usage_message(payload: bytes) -> None:
    _json: dict = json.loads(payload)
    try:
        _message: FilamentUsageDto = FilamentUsageDto.model_validate(_json)
        _usage: CompletedJobDto = _message.job_data
        if _message:
            _filament_usage_repository.save(job_id=str(_usage.job_id),
                                            tag_uid=_message.tag_uid,
                                            filament_usage=_usage.filament_usage)
    except ValidationError as e:
        logging.error(f"Failed to process filament usage message: {e}")

def setup_filament_usage_subscriber(broker, port: int, topic: str) -> bool:
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
    _subscriber.subscribe(topic, _save_filament_usage_message)

    if _subscriber.connect():
        logging.info("Write queue listening on: %s", topic)
        return True

    _subscriber = None
    return False