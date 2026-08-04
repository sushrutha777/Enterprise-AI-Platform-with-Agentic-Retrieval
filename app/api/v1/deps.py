"""FastAPI dependencies and singleton resource injections."""

from typing import Optional
from fastapi import Depends
from app.retriever import BaseRetriever, SparseBM25Retriever, get_default_dense_retriever
from app.services.chat_service import ChatService
from app.core.logging import logger


# Singletons for memory efficiency
_dense_retriever: Optional[BaseRetriever] = None
_sparse_retriever: Optional[SparseBM25Retriever] = None
_chat_service: Optional[ChatService] = None


def get_dense_retriever() -> BaseRetriever:
    global _dense_retriever
    if _dense_retriever is None:
        _dense_retriever = get_default_dense_retriever()
    return _dense_retriever


def get_sparse_retriever() -> SparseBM25Retriever:
    global _sparse_retriever
    if _sparse_retriever is None:
        _sparse_retriever = SparseBM25Retriever()
    return _sparse_retriever


def get_chat_service(
    dense: BaseRetriever = Depends(get_dense_retriever),
    sparse: SparseBM25Retriever = Depends(get_sparse_retriever),
) -> ChatService:
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService(dense, sparse)
    return _chat_service
