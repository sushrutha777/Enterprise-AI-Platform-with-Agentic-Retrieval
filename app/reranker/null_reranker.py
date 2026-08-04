"""Pass-through null reranker."""

from typing import List
from langchain_core.documents import Document
from app.reranker.base import BaseReranker


class NullReranker(BaseReranker):
    """Pass-through reranker when neural reranker is disabled or unavailable."""

    def rerank(self, query: str, documents: List[Document], top_n: int = 5) -> List[Document]:
        return documents[:top_n]
