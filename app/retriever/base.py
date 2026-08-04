"""Base retriever interface."""

from abc import ABC, abstractmethod
from typing import List
from langchain_core.documents import Document


class BaseRetriever(ABC):
    """Abstract base class for document retrievers."""

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 4) -> List[Document]:
        """Retrieve relevant documents for a query."""
        pass
