from abc import ABC, abstractmethod

from openprinttag_rpi.models.domain import FilamentUsageMessage


class FilamentUsageMessageRepository(ABC):
    _sql_table: str = "filament_usage_message"

    @abstractmethod
    def save(
        self,
        job_id: str,
        tag_uid: str,
        filament_usage: float,
        status: str = "NOT_PROCESSED",
    ) -> int:
        """Saves a filament usage message to the database."""

    @abstractmethod
    def find_by_status_and_by_tag_uid(
        self, tag_uid: str, status: str = "NOT_PROCESSED"
    ) -> list[FilamentUsageMessage]:
        """Finds all filament usage messages for a given tag UID and status."""

    @abstractmethod
    def update(
        self, filament_usage_message: FilamentUsageMessage
    ) -> FilamentUsageMessage:
        """Updates the  filament usage message identified by job_id and tag_uid."""

    @abstractmethod
    def get_usage_by_tag_uid_status(
        self, tag_uid: str, status: str = "NOT_PROCESSED"
    ) -> float:
        """Gets the total filament usage for a given tag UID and status."""
