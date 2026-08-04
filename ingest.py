"""Root CLI for Knowledge Ingestion Platform."""

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
    
    if not os.path.exists(directory):
        logger.warning(f"Source directory '{directory}' does not exist.")
        return []
    
    for root, _, files in os.walk(directory):
        for file in files:
            ext = file.split('.')[-1].lower()
            path = os.path.join(root, file)
            
            if ext == "pdf":
                docs = pdf_connector.extract(path)
                documents.extend(docs)
                logger.info(f"Extracted {len(docs)} pages from PDF: {file}")
            elif ext == "txt":
                docs = text_connector.extract(path)
                documents.extend(docs)
                logger.info(f"Extracted {len(docs)} segments from TXT: {file}")
            else:
                logger.debug(f"Skipping unsupported file type: {file}")
                
    return documents

def main():
    parser = argparse.ArgumentParser(description="Knowledge Ingestion Platform CLI")
    parser.add_argument("--source", type=str, default="./data", help="Directory containing files to ingest (default: ./data)")
    parser.add_argument("--reindex", action="store_true", help="Delete the existing Qdrant collection and re-index from scratch")
    parser.add_argument("--incremental", action="store_true", help="Perform incremental indexing (default behavior, deduplicates automatically)")
    
    args = parser.parse_args()

    # Determine if we should drop the collection
    drop_existing = args.reindex
    
    # Initialize stages
    cleaner = DocumentCleaner()
    chunker = SemanticChunker()
    embedder = GeminiEmbedder()
    indexer = QdrantIndexer()
    
    # Ensure collection and optionally drop it
    indexer.ensure_collection(drop_existing=drop_existing)

    logger.info("Initializing Knowledge Ingestion Pipeline...")
    pipeline = IngestionPipeline(
        cleaner=cleaner,
        chunker=chunker,
        embedder=embedder,
        indexer=indexer
    )

    documents = load_documents_from_directory(args.source)
    
    if not documents:
        logger.warning(f"No valid documents found in {args.source}. Pipeline aborted.")
        return
        
    pipeline.process(documents)
    logger.info("Ingestion complete.")

if __name__ == "__main__":
    main()
