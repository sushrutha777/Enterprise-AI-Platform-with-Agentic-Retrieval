"""Dense vector retriever using FAISS and Google Gemini embeddings."""

import os
import time
from typing import List, Optional, Callable
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from app.core.config import settings
from app.core.logging import logger
from app.retriever.base import BaseRetriever


class DenseRetriever(BaseRetriever):
    """Dense retriever powered by FAISS and Gemini embeddings."""

    def __init__(self, api_key: Optional[str] = None):
        key = api_key or settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY")
        if not key:
            raise ValueError("GOOGLE_API_KEY is required for DenseRetriever.")
        
        self.embedding = GoogleGenerativeAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            google_api_key=key,
        )
        self.vectorstore: Optional[FAISS] = None
        self._load_existing_index()

    def _load_existing_index(self):
        """Try loading persisted FAISS index from disk."""
        if os.path.exists(settings.FAISS_INDEX_PATH) and any(os.scandir(settings.FAISS_INDEX_PATH)):
            try:
                self.vectorstore = FAISS.load_local(
                    settings.FAISS_INDEX_PATH,
                    self.embedding,
                    allow_dangerous_deserialization=True,
                )
                logger.info(f"Loaded existing FAISS index from {settings.FAISS_INDEX_PATH}")
            except Exception as e:
                logger.warning(f"Could not load FAISS index: {e}")

    def create_or_update(
        self,
        documents: List[Document],
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ):
        """Create or update FAISS index with batching for free-tier quotas."""
        if not documents:
            return

        batch_size = 10
        total_docs = len(documents)
        total_batches = ((total_docs - 1) // batch_size) + 1

        if progress_callback:
            progress_callback(f"Embedding batch 1/{total_batches}...", 0.0)

        first_batch = documents[:batch_size]
        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(first_batch, self.embedding)
        else:
            self.vectorstore.add_documents(first_batch)

        for i in range(batch_size, total_docs, batch_size):
            batch_num = (i // batch_size) + 1
            if progress_callback:
                progress_callback(f"Embedding batch {batch_num}/{total_batches}...", batch_num / total_batches)
            time.sleep(3)  # Gentle delay to avoid 429 quota exhaustion
            batch = documents[i : i + batch_size]
            self.vectorstore.add_documents(batch)

        # Save to disk
        self.save_index()
        if progress_callback:
            progress_callback("FAISS index saved successfully.", 1.0)

    def save_index(self):
        """Persist FAISS index to disk."""
        if self.vectorstore:
            self.vectorstore.save_local(settings.FAISS_INDEX_PATH)
            logger.info(f"FAISS index saved to {settings.FAISS_INDEX_PATH}")

    def retrieve(self, query: str, top_k: int = 10) -> List[Document]:
        """Retrieve top_k documents by cosine vector similarity."""
        if self.vectorstore is None:
            return []
        try:
            return self.vectorstore.similarity_search(query, k=top_k)
        except Exception as e:
            logger.error(f"Error in dense retrieval: {e}")
            return []

    def get_document_count(self) -> int:
        """Return the count of vectors currently indexed."""
        if self.vectorstore and hasattr(self.vectorstore, "index"):
            return self.vectorstore.index.ntotal
        return 0
