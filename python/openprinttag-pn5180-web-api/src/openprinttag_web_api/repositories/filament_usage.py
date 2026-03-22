""" FilamentUsageRepository repository interface """
from abc import ABC, abstractmethod
from typing import Optional
from openprinttag_web_api.models.domain import FilamentUsageRecord
class FilamentUsageRepository(ABC):
    """Abstract repository for filament usage tracking."""
    
    @abstractmethod
    def save(
        self,
        event_id: int,
        job_id: int,
        filament_g: float,
        tag_id: int,
        job_status: Optional[str] = None,
    ) -> int:
        """Save filament usage record.
        
        Args:
            event_id: Related event ID
            job_id: Print job ID
            filament_g: Filament used in grams
            job_status: Job completion status
            
        Returns:
            ID of created record
        """
    
    @abstractmethod
    def get_usage_by_event(self, event_id: int) -> Optional[FilamentUsageRecord]:
        """Get usage record by event ID."""
    
    @abstractmethod
    def get_total_usage_by_tag_uid(self, tag_uid: str) -> float:
        """Get total filament usage for a tag/spool.
        
        Args:
            tag_uid: Tag UID identifying the spool
            
        Returns:
            Total filament used in grams
        """
