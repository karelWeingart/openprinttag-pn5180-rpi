from openprinttag_rpi.models.domain import FilamentUsageMessage
from openprinttag_rpi.repository.sqlite.filament_usage_message import SqliteFilamentUsageMessageRepository

_filament_usage_message_repository = SqliteFilamentUsageMessageRepository()

def save_filament_usage_message(job_id: str, tag_uid: str, filament_usage: float, status: str = "NOT_PROCESSED") -> int:
    """Saves a filament usage message to the database."""
    return _filament_usage_message_repository.save(
        job_id=job_id,
        tag_uid=tag_uid,
        filament_usage=filament_usage,
        status=status,
    )

def cancel_not_processed_messages_for_tag(tag_uid: str) -> int:
    """Cancels all NOT_PROCESSED messages for a given tag UID."""
    _jobs: list[FilamentUsageMessage] = _filament_usage_message_repository.find_by_status_and_by_tag_uid(tag_uid, "NOT_PROCESSED")
    for job in _jobs:
        job.status = "CANCELED"
        _filament_usage_message_repository.update(job)
    return len(_jobs)

def get_total_filament_usage_by_tag_uid_status(tag_uid: str, status: str = "NOT_PROCESSED") -> float:
    """Gets the total filament usage for a given tag UID and status."""
    return _filament_usage_message_repository.get_usage_by_tag_uid_status(tag_uid, status)