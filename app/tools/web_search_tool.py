"""Web search tool supporting DuckDuckGo and Tavily."""

import os
import asyncio
from typing import Optional
from app.tools.base import BaseAgentTool, ToolResult
from app.core.config import settings
from app.core.logging import logger


class WebSearchTool(BaseAgentTool):
    """Searches the live public internet using DuckDuckGo or Tavily."""

    name = "web_search"
    description = "Searches the live public internet for current events, news, and external facts."

    def __init__(self, tavily_api_key: Optional[str] = None):
        self.tavily_key = tavily_api_key or settings.TAVILY_API_KEY or os.getenv("TAVILY_API_KEY")

    def _search_duckduckgo(self, query: str):
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=3))

    async def run(self, query: str) -> ToolResult:
        if self.tavily_key and not self.tavily_key.startswith("your_"):
            try:
                from langchain_community.tools.tavily_search import TavilySearchResults
                tavily = TavilySearchResults(tavily_api_key=self.tavily_key, max_results=3)
                results = await asyncio.to_thread(tavily.invoke, {"query": query})
                sources = []
                summaries = []
                for res in results:
                    sources.append({
                        "title": res.get("title", "Web Result"),
                        "source_type": "web",
                        "url": res.get("url"),
                        "content": res.get("content", ""),
                    })
                    summaries.append(f"Title: {res.get('title')}\nURL: {res.get('url')}\n{res.get('content')}")
                return ToolResult(
                    tool_name=self.name,
                    source_type="web",
                    output="\n\n".join(summaries),
                    sources=sources,
                )
            except Exception as e:
                logger.warning(f"Tavily search failed ({e}), falling back to DuckDuckGo.")

        # DuckDuckGo Search (Threaded)
        try:
            results = await asyncio.to_thread(self._search_duckduckgo, query)
            sources = []
            summaries = []
            for res in results:
                title = res.get("title", "Web Result")
                url = res.get("href", "")
                body = res.get("body", "")
                sources.append({
                    "title": title,
                    "source_type": "web",
                    "url": url,
                    "content": body,
                })
                summaries.append(f"Title: {title}\nURL: {url}\n{body}")

            return ToolResult(
                tool_name=self.name,
                source_type="web",
                output="\n\n".join(summaries) if summaries else "No relevant web search results found.",
                sources=sources,
            )
        except Exception as e:
            logger.error(f"DuckDuckGo search error for '{query}': {e}")
            return ToolResult(
                tool_name=self.name,
                source_type="web",
                output=f"Error executing web search: {str(e)}",
                sources=[],
            )
