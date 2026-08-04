"""Retriever package export and factory loader."""

from app.retriever.base import BaseRetriever
from app.retriever.qdrant_retriever import QdrantRetriever
from app.retriever.dense import DenseRetriever
from app.retriever.sparse import SparseBM25Retriever
from app.retriever.hybrid import HybridRetriever
from app.core.config import settings
from app.core.logging import logger


def get_default_dense_retriever() -> BaseRetriever:
    """Instantiate configured dense retriever (Qdrant by default in production, FAISS as fallback)."""
    if settings.VECTOR_DB_TYPE.lower() == "qdrant":
        try:
            logger.info("Initializing production Qdrant vector database retriever.")
            return QdrantRetriever()
        except Exception as e:
            logger.warning(f"Failed to initialize Qdrant ({e}), falling back to FAISS.")
            return DenseRetriever()
    else:
        return DenseRetriever()


__all__ = [
    "BaseRetriever",
    "QdrantRetriever",
    "DenseRetriever",
    "SparseBM25Retriever",
    "HybridRetriever",
    "get_default_dense_retriever",
]
