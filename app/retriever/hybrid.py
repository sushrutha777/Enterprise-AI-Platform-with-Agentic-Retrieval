"""Hybrid retriever combining Dense vector search (Qdrant / FAISS) and Sparse BM25 via Reciprocal Rank Fusion (RRF)."""

from typing import List, Dict
from langchain_core.documents import Document
from app.core.config import settings
from app.core.logging import logger
from app.retriever.base import BaseRetriever
from app.retriever.sparse import SparseBM25Retriever


class HybridRetriever(BaseRetriever):
    """Combines dense semantic search and sparse keyword search using Reciprocal Rank Fusion (RRF)."""

    def __init__(self, dense_retriever: BaseRetriever, sparse_retriever: SparseBM25Retriever, rrf_k: int = 60):
        self.dense = dense_retriever
        self.sparse = sparse_retriever
        self.rrf_k = rrf_k

    def retrieve(self, query: str, top_k: int = 15) -> List[Document]:
        """Execute hybrid search with Reciprocal Rank Fusion."""
        # 1. Retrieve candidates from both systems
        dense_docs = self.dense.retrieve(query, top_k=top_k)
        sparse_docs = self.sparse.retrieve(query, top_k=top_k)

        if not dense_docs and not sparse_docs:
            return []
        if not dense_docs:
            return sparse_docs[:top_k]
        if not sparse_docs:
            return dense_docs[:top_k]

        # 2. Compute RRF scores
        rrf_scores: Dict[str, float] = {}
        doc_map: Dict[str, Document] = {}

        # Process dense results
        for rank, doc in enumerate(dense_docs):
            key = doc.page_content.strip()
            doc_map[key] = doc
            rrf_scores[key] = rrf_scores.get(key, 0.0) + (1.0 / (self.rrf_k + rank + 1))

        # Process sparse results
        for rank, doc in enumerate(sparse_docs):
            key = doc.page_content.strip()
            doc_map[key] = doc
            rrf_scores[key] = rrf_scores.get(key, 0.0) + (1.0 / (self.rrf_k + rank + 1))

        # 3. Sort by aggregated RRF score
        sorted_keys = sorted(rrf_scores.keys(), key=lambda k: rrf_scores[k], reverse=True)
        fused_docs = [doc_map[k] for k in sorted_keys[:top_k]]
        
        logger.info(f"Hybrid search fused {len(dense_docs)} dense + {len(sparse_docs)} sparse into {len(fused_docs)} candidates.")
        return fused_docs
