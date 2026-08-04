"""Pipeline orchestrator for the Knowledge Ingestion Platform."""

from typing import List
from ingestion_platform.core.models import StandardDocument
from app.core.logging import logger

class IngestionPipeline:
    """
    DAG orchestrator that processes documents through strict stages:
    Extract -> Clean -> Normalize -> Chunk -> Embed -> Index
    """

    def __init__(self, cleaner, chunker, embedder, indexer):
        self.cleaner = cleaner
        self.chunker = chunker
        self.embedder = embedder
        self.indexer = indexer

    def process(self, documents: List[StandardDocument]) -> None:
        """Process a batch of extracted documents through the pipeline."""
        if not documents:
            logger.info("No documents provided to pipeline.")
            return

        total = len(documents)
        logger.info(f"Starting ingestion pipeline for {total} documents.")

        # Stage 1: Clean & Normalize
        logger.info("Stage 1: Cleaning & Normalizing...")
        cleaned_docs = []
        for doc in documents:
            doc.content = self.cleaner.clean(doc.content)
            cleaned_docs.append(doc)

        # Stage 2: Chunk
        logger.info("Stage 2: Chunking...")
        for doc in cleaned_docs:
            doc.chunks = self.chunker.chunk(doc.content)
            logger.debug(f"Document {doc.source_id} split into {len(doc.chunks)} chunks.")

        # Stage 3: Metadata Extraction (Placeholder for future NLP extraction)
        # E.g., extracting named entities, dates, authors to add to doc.metadata

        # Stage 4: Embed
        logger.info("Stage 4: Generating Embeddings...")
        for doc in cleaned_docs:
            if doc.chunks:
                doc.embeddings = self.embedder.embed(doc.chunks)

        # Stage 5: Index
        logger.info("Stage 5: Indexing into Vector Database...")
        self.indexer.index(cleaned_docs)

        logger.info(f"Ingestion pipeline completed successfully for {total} documents.")
