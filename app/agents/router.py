"""Rule-based, zero-LLM tool router."""

import re
from typing import List, Tuple
from pydantic import BaseModel
from app.core.logging import logger

class RoutingDecision(BaseModel):
    tools: List[str]
    needs_llm: bool
    intent: str

class AgentRouter:
    """Fast, heuristic-based router to select tools without LLM latency."""

    @staticmethod
    def route(question: str) -> RoutingDecision:
        q_lower = question.lower()

        # 1. Direct Intents (No retrieval needed)
        greetings = [
            "hi", "hello", "hey", "good morning", "good evening", 
            "good afternoon", "greetings", "howdy", "hola", "yo"
        ]
        farewells = ["bye", "goodbye", "see you", "cya", "farewell", "take care"]
        casual = [
            "how are you", "who are you", "what are you", "thank you", 
            "thanks", "good job", "who made you", "what can you do", "help"
        ]

        if any(q_lower == g or q_lower.startswith(g + " ") for g in greetings):
            return RoutingDecision(tools=[], needs_llm=True, intent="greeting")
        
        if any(q_lower == f or q_lower.startswith(f + " ") for f in farewells):
            return RoutingDecision(tools=[], needs_llm=True, intent="farewell")
            
        if any(c in q_lower for c in casual):
            return RoutingDecision(tools=[], needs_llm=True, intent="casual")

        # 2. Knowledge Query Routing
        tools = []
        
        # Real-time / temporal / dynamic web triggers
        time_patterns = [
            r"\b20\d{2}\b", r"\btoday\b", r"\bnow\b", r"\bcurrent\b", 
            r"\brecent\b", r"\blatest\b", r"\bnews\b", r"\bweather\b", 
            r"\bstock\b", r"\bprice\b", r"\btonight\b", r"\byesterday\b"
        ]
        if any(re.search(p, q_lower) for p in time_patterns):
            tools.append("web_search")

        # Encyclopedic / historical triggers
        wiki_patterns = [
            "who is", "who was", "what is the history", "where is", 
            "biography", "born", "invented", "founded in", "capital of"
        ]
        if any(w in q_lower for w in wiki_patterns):
            tools.append("wikipedia")
            
        # Domain documentation / specific terminology triggers
        doc_patterns = [
            "explain", "how does", "what does", "define", "according to",
            "document", "uploaded", "pdf", "file", "policy", "manual", "report"
        ]
        if any(d in q_lower for d in doc_patterns):
            tools.append("document_search")

        # Fallback to parallel execution of web + docs if uncertain
        if not tools:
            tools = ["document_search", "web_search"]
            
        # Deduplicate while preserving order
        deduped_tools = list(dict.fromkeys(tools))

        return RoutingDecision(tools=deduped_tools, needs_llm=True, intent="knowledge")
