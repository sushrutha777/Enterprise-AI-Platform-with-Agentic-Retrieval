"""Chunker stage for the ingestion pipeline."""

from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter

class SemanticChunker:
    """Splits text into semantic chunks."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""],
        )

    def chunk(self, text: str) -> List[str]:
        """
        Splits a single large text string into multiple smaller semantic chunks.
        """
        if not text:
            return []
            
        return self.text_splitter.split_text(text)
