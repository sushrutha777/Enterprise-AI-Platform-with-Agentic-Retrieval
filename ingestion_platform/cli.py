"""Command line interface for the independent Knowledge Ingestion Platform."""

import os
import argparse
from typing import List

from ingestion_platform.core.pipeline import IngestionPipeline
from ingestion_platform.core.models import StandardDocument
from ingestion_platform.connectors.pdf import PDFConnector
from ingestion_platform.connectors.text import TextConnector
from ingestion_platform.stages.cleaner import DocumentCleaner
from ingestion_platform.stages.chunker import SemanticChunker
from ingestion_platform.stages.embedder import GeminiEmbedder
from ingestion_platform.stages.indexer import QdrantIndexer
from app.core.logging import setup_logging

logger = setup_logging()

def load_documents_from_directory(directory: str) -> List[StandardDocument]:
    """Scans a directory and uses the appropriate connector to load documents."""
    pdf_connector = PDFConnector()
    text_connector = TextConnector()
    
    documents = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            ext = file.split('.')[-1].lower()
            path = os.path.join(root, file)
            
            if ext == "pdf":
                docs = pdf_connector.extract(path)
                documents.extend(docs)
                logger.info(f"Extracted {len(docs)} pages from PDF: {file}")
            elif ext in ["txt", "md", "markdown"]:
                docs = text_connector.extract(path)
                documents.extend(docs)
                logger.info(f"Extracted {len(docs)} segments from {ext.upper()}: {file}")
            else:
                logger.debug(f"Skipping unsupported file type: {file}")
                
    return documents

def main():
    parser = argparse.ArgumentParser(description="Knowledge Ingestion Platform CLI")
    parser.add_argument("directory", type=str, help="Directory containing files to ingest")
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        logger.error(f"Directory not found: {args.directory}")
        return

    logger.info("Initializing Knowledge Ingestion Pipeline...")
    pipeline = IngestionPipeline(
        cleaner=DocumentCleaner(),
        chunker=SemanticChunker(),
        embedder=GeminiEmbedder(),
        indexer=QdrantIndexer()
    )

    documents = load_documents_from_directory(args.directory)
    
    if not documents:
        logger.warning(f"No valid documents found in {args.directory}")
        return
        
    pipeline.process(documents)
    logger.info("Ingestion complete.")

if __name__ == "__main__":
    main()
