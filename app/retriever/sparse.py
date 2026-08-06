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


import os
from pathlib import Path


class SparseBM25Retriever(BaseRetriever):
    """Sparse keyword retriever using BM25 algorithm."""

    def __init__(self, documents: Optional[List[Document]] = None, data_dir: Optional[str] = None):
        self.documents: List[Document] = []
        self.bm25: Optional[BM25Okapi] = None
        if documents:
            self.index_documents(documents)
        else:
            self.load_from_data_dir(data_dir or "./data")

    def load_from_data_dir(self, data_dir: str):
        """Loads and indexes all .txt, .md, and .pdf documents from data directory."""
        if not os.path.isdir(data_dir):
            return

        loaded_docs: List[Document] = []
        for root, _, files in os.walk(data_dir):
            for file in files:
                path = os.path.join(root, file)
                ext = file.split(".")[-1].lower()
                try:
                    if ext in ["txt", "md", "markdown"]:
                        with open(path, "r", encoding="utf-8", errors="ignore") as f:
                            text = f.read()
                        if text.strip():
                            # Chunk by paragraphs/sections for granular BM25 matching
                            sections = [s.strip() for s in text.split("\n\n") if len(s.strip()) > 30]
                            if not sections:
                                sections = [text]
                            for sec in sections:
                                loaded_docs.append(Document(page_content=sec, metadata={"source": file}))
                    elif ext == "pdf":
                        try:
                            from pypdf import PdfReader
                            reader = PdfReader(path)
                            for page_idx, page in enumerate(reader.pages):
                                page_text = page.extract_text()
                                if page_text and page_text.strip():
                                    loaded_docs.append(Document(page_content=page_text.strip(), metadata={"source": file, "page": page_idx + 1}))
                        except Exception as pdf_err:
                            logger.debug(f"PDF extraction note for {file}: {pdf_err}")
                except Exception as file_err:
                    logger.warning(f"Failed to read {file} for BM25: {file_err}")

        if loaded_docs:
            self.index_documents(loaded_docs)

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
