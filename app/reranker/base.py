"""Base reranker interface."""

from abc import ABC, abstractmethod
from typing import List
from langchain_core.documents import Document


class BaseReranker(ABC):
    """Abstract base class for document rerankers."""

    @abstractmethod
    def rerank(self, query: str, documents: List[Document], top_n: int = 5) -> List[Document]:
        """Rerank candidate documents based on relevance to query."""
        pass
