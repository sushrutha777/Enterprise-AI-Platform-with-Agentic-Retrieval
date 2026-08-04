"""Indexer stage for the ingestion pipeline to Qdrant."""

import uuid
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from ingestion_platform.core.models import StandardDocument
from app.core.config import settings
from app.core.logging import logger

class QdrantIndexer:
    """Indexes documents directly into Qdrant."""
    
    def __init__(self):
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        
        if settings.QDRANT_URL:
            self.client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
            )
        else:
            self.client = QdrantClient(path=settings.QDRANT_PATH)

    def ensure_collection(self, drop_existing: bool = False):
        if drop_existing:
            logger.info(f"Dropping existing Qdrant collection: {self.collection_name}")
            self.client.delete_collection(self.collection_name)
            
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        
        if not exists:
            logger.info(f"Creating Qdrant collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
            )

    def index(self, documents: List[StandardDocument]) -> None:
        """
        Indexes standard documents.
        Checks `content_hash` to avoid re-indexing exact duplicates.
        """
        points = []
        for doc in documents:
            if not doc.chunks or not doc.embeddings:
                continue
                
            for chunk_text, embedding in zip(doc.chunks, doc.embeddings):
                # Unique ID per chunk
                point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, doc.content_hash + chunk_text))
                
                payload = {
                    "page_content": chunk_text,
                    "metadata": doc.metadata,
                    "content_hash": doc.content_hash,
                    "source_id": doc.source_id,
                    "connector_type": doc.connector_type
                }
                
                points.append(PointStruct(id=point_id, vector=embedding, payload=payload))
                
        if points:
            # Upsert overwrites existing point IDs, providing idempotency
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i+batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
            logger.info(f"Upserted {len(points)} total vectors into Qdrant.")
