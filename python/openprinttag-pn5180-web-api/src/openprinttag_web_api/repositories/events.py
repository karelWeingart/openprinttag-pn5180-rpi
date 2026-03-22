from abc import ABC, abstractmethod
from typing import Optional
from openprinttag_web_api.models.domain import EventWithTag


class EventRepository(ABC):
    """Abstract repository for events."""

    @abstractmethod
    def save(
        self,
        event_type: str,
        tag_id: Optional[int] = None,
        success: bool = True,
    ) -> int:
        """Save a new event.

        Args:
            event_type: Type of event
            tag_id: Related tag ID (optional)
            success: Whether event was successful

        Returns:
            ID of created event
        """

    @abstractmethod
    def get_by_id(self, event_id: int) -> Optional[EventWithTag]:
        """Get event by ID with tag data."""

    @abstractmethod
    def list_all(
        self,
        page: int = 1,
        page_size: int = 50,
        event_type: Optional[str] = None,
        success: Optional[bool] = None,
    ) -> tuple[list[EventWithTag], int]:
        """List events with pagination and filters.

        Returns:
            Tuple of (events, total_count)
        """

    @abstractmethod
    def get_by_tag_uid(self, tag_uid: str) -> list[EventWithTag]:
        """Get all events for a tag UID."""

    @abstractmethod
    def get_last_event_by_event_type(self, event_type: str) -> Optional[EventWithTag]:
        """Returns last event by type."""
