"""Neural cross-encoder reranker using FlashRank."""

import os
import tempfile
from typing import List, Optional
from langchain_core.documents import Document
from app.core.logging import logger
from app.reranker.base import BaseReranker


class FlashRankReranker(BaseReranker):
    """Local, lightweight neural reranker using FlashRank (ms-marco-TinyBERT)."""

    def __init__(self, model_name: str = "ms-marco-TinyBERT-L-2-v2"):
        self.model_name = model_name
        self.ranker = None
        try:
            from flashrank import Ranker
            cache_dir = os.path.join(tempfile.gettempdir(), "flashrank_cache")
            self.ranker = Ranker(model_name=model_name, cache_dir=cache_dir)
            logger.info(f"FlashRank reranker initialized with {model_name}")
        except Exception as e:
            logger.warning(f"FlashRank initialization failed ({e}). Fallback to pass-through.")

    def rerank(
        self,
        query: str,
        documents: List[Document],
        top_n: int = 5,
        top_k: Optional[int] = None,
    ) -> List[Document]:
        """Rerank candidate documents using FlashRank cross-encoder."""
        limit = top_k if top_k is not None else top_n
        if not documents:
            return []
        if len(documents) <= limit or self.ranker is None:
            return documents[:limit]

        try:
            from flashrank import RerankRequest

            passages = [
                {"id": idx, "text": doc.page_content, "meta": doc.metadata}
                for idx, doc in enumerate(documents)
            ]

            rerank_request = RerankRequest(query=query, passages=passages)
            results = self.ranker.rerank(rerank_request)

            reranked_docs = []
            for res in results[:limit]:
                original_idx = res["id"]
                doc = documents[original_idx]
                doc.metadata["rerank_score"] = float(res.get("score", 0.0))
                reranked_docs.append(doc)

            logger.info(f"FlashRank reranked {len(documents)} down to {len(reranked_docs)} high-relevance chunks.")
            return reranked_docs
        except Exception as e:
            logger.error(f"Error during FlashRank reranking: {e}. Returning unranked top_n.")
            return documents[:limit]
