"""Document retriever tool powered by Hybrid Search and Neural Reranking."""

import asyncio
from typing import Optional
from app.tools.base import BaseAgentTool, ToolResult
from app.retriever.hybrid import HybridRetriever
from app.reranker.base import BaseReranker
from app.core.config import settings
from app.core.logging import logger


class DocumentRetrieverTool(BaseAgentTool):
    """Retrieves document chunks from indexed knowledge base."""

    name = "document_search"
    description = "Searches the uploaded PDF, TXT, and Markdown knowledge base for factual information."

    def __init__(self, hybrid_retriever: HybridRetriever, reranker: Optional[BaseReranker] = None):
        self.retriever = hybrid_retriever
        self.reranker = reranker

    async def run(self, query: str) -> ToolResult:
        """Retrieve and rerank document chunks."""
        # Wrap the synchronous retrieval in run_in_executor
        candidates = await asyncio.to_thread(self.retriever.retrieve, query, top_k=settings.RETRIEVAL_TOP_K)

        if not candidates:
            return ToolResult(
                tool_name=self.name,
                source_type="document",
                output="No relevant documents found in the local knowledge base.",
                sources=[],
            )

        if self.reranker:
            final_docs = await asyncio.to_thread(self.reranker.rerank, query, candidates, top_n=settings.RERANKED_TOP_K)
        else:
            final_docs = candidates[:settings.RERANKED_TOP_K]

        sources = []
        context_parts = []
        for idx, doc in enumerate(final_docs):
            filename = doc.metadata.get("source", "Uploaded Document")
            page = doc.metadata.get("page", None)
            score = doc.metadata.get("rerank_score", None)

            sources.append({
                "title": filename.split("/")[-1].split("\\")[-1],
                "source_type": "document",
                "page": page + 1 if isinstance(page, int) else None,
                "chunk_index": idx + 1,
                "score": score,
                "content": doc.page_content.strip(),
            })

            page_info = f" (Page {page + 1})" if isinstance(page, int) else ""
            context_parts.append(f"[{idx + 1}] Source: {filename}{page_info}\n{doc.page_content}")

        return ToolResult(
            tool_name=self.name,
            source_type="document",
            output="\n\n".join(context_parts),
            sources=sources,
        )
