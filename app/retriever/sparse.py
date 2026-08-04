"""Sparse keyword retriever using BM25Okapi."""

import re
from typing import List, Optional
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi
from app.core.logging import logger
from app.retriever.base import BaseRetriever


def tokenize(text: str) -> List[str]:
    """Tokenize lowercase alphanumeric words."""
    return re.findall(r"\w+", text.lower())


class SparseBM25Retriever(BaseRetriever):
    """Sparse keyword retriever using BM25 algorithm."""

    def __init__(self, documents: Optional[List[Document]] = None):
        self.documents: List[Document] = []
        self.bm25: Optional[BM25Okapi] = None
        if documents:
            self.index_documents(documents)

    def index_documents(self, documents: List[Document]):
        """Build or update BM25 inverted index."""
        if not documents:
            return
        self.documents = documents
        corpus = [tokenize(doc.page_content) for doc in documents]
        self.bm25 = BM25Okapi(corpus)
        logger.info(f"BM25 index built with {len(documents)} document chunks.")

    def retrieve(self, query: str, top_k: int = 10) -> List[Document]:
        """Retrieve top_k documents by BM25 keyword matching score."""
        if not self.bm25 or not self.documents:
            return []

        tokens = tokenize(query)
        if not tokens:
            return []

        try:
            scores = self.bm25.get_scores(tokens)
            # Pair scores with documents
            scored_docs = sorted(zip(scores, self.documents), key=lambda x: x[0], reverse=True)
            # Filter out docs with 0 score
            non_zero = [doc for score, doc in scored_docs if score > 0]
            return non_zero[:top_k]
        except Exception as e:
            logger.error(f"Error in BM25 retrieval: {e}")
            return []
