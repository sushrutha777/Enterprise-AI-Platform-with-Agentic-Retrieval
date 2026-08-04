"""Text connector for the ingestion pipeline."""

import os
from typing import List
from langchain_community.document_loaders import TextLoader
from ingestion_platform.connectors.base import BaseConnector
from ingestion_platform.core.models import StandardDocument
from app.core.logging import logger

class TextConnector(BaseConnector):
    """Extracts text from TXT files."""

    def extract(self, source: str) -> List[StandardDocument]:
        """
        Extracts content from a TXT file path.
        """
        if not os.path.exists(source) or not source.lower().endswith(".txt"):
            logger.error(f"Invalid TXT source: {source}")
            return []

        try:
            loader = TextLoader(source)
            raw_docs = loader.load()
            
            standard_docs = []
            for i, doc in enumerate(raw_docs):
                standard_docs.append(StandardDocument(
                    content=doc.page_content,
                    source_id=f"{source}_chunk_{i+1}",
                    connector_type="text",
                    metadata={
                        "original_source": source,
                        "source_type": "file_txt"
                    }
                ))
            return standard_docs
            
        except Exception as e:
            logger.error(f"Error extracting TXT {source}: {e}")
            return []
