from abc import ABC, abstractmethod
from typing import Optional
from openprinttag_web_api.models.domain import TagRecord

class TagRepository(ABC):
    """Abstract repository for tag data."""
    
    @abstractmethod
    def save(self, tag_uid: str, data: str) -> int:
        """Save or update tag data.
        
        Args:
            tag_uid: Tag UID
            data: JSON string of tag data
            
        Returns:
            ID of created/updated record
        """
    
    @abstractmethod
    def get_by_uid(self, tag_uid: str) -> Optional[TagRecord]:
        """Get latest tag data by UID."""
    
    @abstractmethod
    def get_by_id(self, tag_id: int) -> Optional[TagRecord]:
        """Get tag by database ID."""
    
    @abstractmethod
    def list_all(
        self,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[TagRecord], int]:
        """List all tags with pagination.
        
        Returns:
            Tuple of (tags, total_count)
        """
    
    @abstractmethod
    def count_unique(self) -> int:
        """Count unique tag UIDs."""
