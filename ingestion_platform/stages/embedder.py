"""Embedder stage for the ingestion pipeline."""

import os
from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.core.config import settings

class GeminiEmbedder:
    """Generates vector embeddings using Google Gemini."""
    
    def __init__(self):
        key = settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY")
        if not key:
            raise ValueError("GOOGLE_API_KEY is required for Embedder.")
            
        self.embedding_model = GoogleGenerativeAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            google_api_key=key,
        )

    def embed(self, chunks: List[str]) -> List[List[float]]:
        """
        Generates a list of vector embeddings for a list of text chunks.
        """
        if not chunks:
            return []
            
        # The underlying library handles batching, but for huge lists we might 
        # want to add explicit rate-limit safe batching here later.
        return self.embedding_model.embed_documents(chunks)
