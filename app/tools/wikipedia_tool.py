"""Wikipedia search tool."""

import wikipedia
import asyncio
from app.tools.base import BaseAgentTool, ToolResult
from app.core.logging import logger


class WikipediaSearchTool(BaseAgentTool):
    """Searches Wikipedia encyclopedia for general knowledge."""

    name = "wikipedia"
    description = "Searches Wikipedia for encyclopedic and historical knowledge."

    async def run(self, query: str) -> ToolResult:
        try:
            wikipedia.set_lang("en")
            search_results = await asyncio.to_thread(wikipedia.search, query, results=2)
            if not search_results:
                return ToolResult(
                    tool_name=self.name,
                    source_type="wikipedia",
                    output="No Wikipedia articles found matching the query.",
                    sources=[],
                )

            title = search_results[0]
            summary = await asyncio.to_thread(wikipedia.summary, title, sentences=5, auto_suggest=False)
            page = await asyncio.to_thread(wikipedia.page, title, auto_suggest=False)

            source = {
                "title": f"Wikipedia: {title}",
                "source_type": "wikipedia",
                "url": page.url,
                "content": summary,
            }

            return ToolResult(
                tool_name=self.name,
                source_type="wikipedia",
                output=f"Wikipedia Article: '{title}'\nURL: {page.url}\n\nSummary:\n{summary}",
                sources=[source],
            )
        except Exception as e:
            logger.warning(f"Wikipedia search error for '{query}': {e}")
            return ToolResult(
                tool_name=self.name,
                source_type="wikipedia",
                output=f"Could not retrieve Wikipedia article: {str(e)}",
                sources=[],
            )
