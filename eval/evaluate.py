"""Evaluation script for assessing RAG latency and accuracy."""

import asyncio
import time
from typing import List, Dict
from app.agents.orchestrator import AgentOrchestrator
from app.retriever import get_default_dense_retriever, SparseBM25Retriever, HybridRetriever
from app.reranker.null_reranker import NullReranker
from app.tools.base import ToolRegistry
from app.tools.retriever_tool import DocumentRetrieverTool

# Example dataset
TEST_CASES = [
    {"query": "Hello there", "expected_intent": "greeting"},
    {"query": "What is the capital of France?", "expected_intent": "knowledge"},
]

async def run_eval():
    print("Starting evaluation...")
    
    dense = get_default_dense_retriever()
    sparse = SparseBM25Retriever()
    hybrid = HybridRetriever(dense, sparse)
    reranker = NullReranker()
    
    registry = ToolRegistry()
    registry.register(DocumentRetrieverTool(hybrid, reranker))
    
    orchestrator = AgentOrchestrator(registry)
    
    for idx, tc in enumerate(TEST_CASES):
        print(f"\n--- Test Case {idx+1} ---")
        print(f"Query: {tc['query']}")
        
        start_time = time.time()
        
        final_answer = ""
        intent = "unknown"
        
        async for event in orchestrator.stream_chat(tc["query"], session_id=f"eval_sess_{idx}"):
            if event["type"] == "metadata":
                intent = event.get("intent", "unknown")
            elif event["type"] == "token":
                final_answer += event["token"]
                
        latency = round(time.time() - start_time, 2)
        
        print(f"Intent detected: {intent} (Expected: {tc['expected_intent']})")
        print(f"Latency: {latency}s")
        print(f"Answer snippet: {final_answer[:100]}...")
        
if __name__ == "__main__":
    asyncio.run(run_eval())
