"""Retriever package export and factory loader."""

from app.retriever.base import BaseRetriever
from app.retriever.qdrant_retriever import QdrantRetriever
from app.retriever.sparse import SparseBM25Retriever
from app.retriever.hybrid import HybridRetriever
from app.core.config import settings
from app.core.logging import logger


def get_default_dense_retriever() -> BaseRetriever:
    """Instantiate configured dense retriever (Qdrant)."""
    if settings.VECTOR_DB_TYPE.lower() == "qdrant":
        try:
            logger.info("Initializing production Qdrant vector database retriever.")
            return QdrantRetriever()
        except Exception as e:
            error_msg = f"Failed to initialize Qdrant ({e}). Developer Notification: Please ensure Qdrant Cloud or local instance is running and configured correctly."
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    else:
        raise ValueError(f"Unsupported VECTOR_DB_TYPE: {settings.VECTOR_DB_TYPE}. Only 'qdrant' is supported in this configuration.")


__all__ = [
    "BaseRetriever",
    "QdrantRetriever",
    "SparseBM25Retriever",
    "HybridRetriever",
    "get_default_dense_retriever",
]
