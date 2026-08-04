"""PDF connector for the ingestion pipeline."""

import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from ingestion_platform.connectors.base import BaseConnector
from ingestion_platform.core.models import StandardDocument
from app.core.logging import logger

class PDFConnector(BaseConnector):
    """Extracts text from PDF files using PyPDFLoader."""

    def extract(self, source: str) -> List[StandardDocument]:
        """
        Extracts content from a PDF file path.
        """
        if not os.path.exists(source) or not source.lower().endswith(".pdf"):
            logger.error(f"Invalid PDF source: {source}")
            return []

        try:
            loader = PyPDFLoader(source)
            raw_docs = loader.load()
            
            standard_docs = []
            for i, doc in enumerate(raw_docs):
                standard_docs.append(StandardDocument(
                    content=doc.page_content,
                    source_id=f"{source}_page_{i+1}",
                    connector_type="pdf",
                    metadata={
                        "original_source": source,
                        "page": i + 1,
                        "source_type": "file_pdf"
                    }
                ))
            return standard_docs
            
        except Exception as e:
            logger.error(f"Error extracting PDF {source}: {e}")
            return []
