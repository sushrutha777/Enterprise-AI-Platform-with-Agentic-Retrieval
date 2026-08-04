"""Core data models for the ingestion pipeline."""

from dataclasses import dataclass, field
from typing import Dict, Any, List
import hashlib

@dataclass
class StandardDocument:
    """Standardized document representation passed between pipeline stages."""
    
    # Core content
    content: str
    
    # Identifiers
    source_id: str  # e.g., URL, file path, database row ID
    connector_type: str  # 'pdf', 'website', 'sql', etc.
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Processed states
    chunks: List[str] = field(default_factory=list)
    embeddings: List[List[float]] = field(default_factory=list)
    
    @property
    def content_hash(self) -> str:
        """MD5 hash of the raw content to detect duplicates/changes."""
        return hashlib.md5(self.content.encode("utf-8")).hexdigest()
