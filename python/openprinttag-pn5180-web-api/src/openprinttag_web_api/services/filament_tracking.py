"""Filament tracking service."""

from typing import Optional

from openprinttag_web_api.repositories.filament_usage import FilamentUsageRepository
from openprinttag_web_api.repositories.sqlite.filament_usage import (
    SqliteFilamentUsageRepository,
)
from openprinttag_web_api.repositories.events import EventRepository
from openprinttag_web_api.repositories.sqlite.events import SqliteEventRepository
from openprinttag_shared.models.dto import CompletedJobDto
from openprinttag_web_api.models.domain import EventWithTag
from openprinttag_web_api.integrations.mqtt.filament_usage_publisher import (
    publish_filament_usage_data,
)


class FilamentTrackingService:
    """Service for tracking filament usage across print jobs."""

    def __init__(
        self,
        repository: Optional[FilamentUsageRepository] = None,
        event_repository: Optional[EventRepository] = None,
    ):
        """Initialize with repository.

        Args:
            repository: Repository implementation. Defaults to SQLite.
        """
        self._repository = repository or SqliteFilamentUsageRepository()
        self._event_repository = event_repository or SqliteEventRepository()

    def record_job_completion(
        self,
        job: CompletedJobDto,
    ) -> int:
        """Record filament usage from a completed job.

        Args:
            job: Completed job data
            event_id: Related event ID in database

        Returns:
            ID of created usage record
        """
        _last_loaded_spool_event: EventWithTag | None = (
            self._event_repository.get_last_event_by_event_type("success_read")
        )

        if not _last_loaded_spool_event or not _last_loaded_spool_event.tag_uid:
            return 0

        publish_filament_usage_data(job, _last_loaded_spool_event.tag_uid)

        return self._repository.save(
            event_id=_last_loaded_spool_event.id,
            tag_id=_last_loaded_spool_event.tag_id or 0,
            job_id=job.job_id,
            filament_g=job.used_filament_g or 0.0,
            job_status=job.end_reason,
        )

    def get_total_usage(self, tag_uid: str) -> float:
        """Get total filament used from a spool.

        Args:
            tag_uid: Tag UID identifying the spool

        Returns:
            Total filament used in grams
        """
        return self._repository.get_total_usage_by_tag_uid(tag_uid)


# Default service instance
filament_tracking = FilamentTrackingService()
