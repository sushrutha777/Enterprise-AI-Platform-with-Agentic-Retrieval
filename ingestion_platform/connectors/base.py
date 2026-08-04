"""Base connector interface for the ingestion pipeline."""

from abc import ABC, abstractmethod
from typing import List, Any
from ingestion_platform.core.models import StandardDocument

class BaseConnector(ABC):
    """
    Abstract base class for all knowledge ingestion connectors.
    Enforces a standard output format (StandardDocument) regardless of input source.
    """

    @abstractmethod
    def extract(self, source: Any) -> List[StandardDocument]:
        """
        Extracts content from a specific source.
        
        Args:
            source: The input source (e.g., file path, URL, database connection string)
            
        Returns:
            List[StandardDocument]: A list of standardized documents ready for processing.
        """
        pass
