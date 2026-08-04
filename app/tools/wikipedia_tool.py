"""Wikipedia search tool."""

import re
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
            # Clean context wrapper if present
            cleaned_query = re.sub(r"\(Context:\s*in reference to\s*['\"].*?['\"]\)", "", query, flags=re.IGNORECASE).strip()
            if not cleaned_query:
                cleaned_query = query
            
            # Remove punctuation that might disrupt Wikipedia search API
            search_term = re.sub(r"[^\w\s\-]", " ", cleaned_query).strip()
            search_results = await asyncio.to_thread(wikipedia.search, search_term or query, results=5)
            
            if not search_results:
                return ToolResult(
                    tool_name=self.name,
                    source_type="wikipedia",
                    output="No Wikipedia articles found matching the query.",
                    sources=[],
                )

            # Try candidate titles until one succeeds cleanly
            for title in search_results:
                try:
                    summary = await asyncio.to_thread(wikipedia.summary, title, sentences=6, auto_suggest=True)
                    page = await asyncio.to_thread(wikipedia.page, title, auto_suggest=True)

                    if summary and page and page.url:
                        source = {
                            "title": f"Wikipedia: {page.title or title}",
                            "source_type": "wikipedia",
                            "url": page.url,
                            "content": summary,
                        }

                        return ToolResult(
                            tool_name=self.name,
                            source_type="wikipedia",
                            output=f"Wikipedia Article: '{page.title or title}'\nURL: {page.url}\n\nSummary:\n{summary}",
                            sources=[source],
                        )
                except (wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError) as pe:
                    logger.debug(f"Wikipedia candidate '{title}' failed: {pe}. Trying next...")
                    continue
                except Exception as ex:
                    logger.warning(f"Wikipedia fetch error for '{title}': {ex}")
                    continue

            return ToolResult(
                tool_name=self.name,
                source_type="wikipedia",
                output=f"Could not retrieve a valid Wikipedia page for query '{query}'.",
                sources=[],
            )
        except Exception as e:
            logger.warning(f"Wikipedia search error for '{query}': {e}")
            return ToolResult(
                tool_name=self.name,
                source_type="wikipedia",
                output=f"Could not retrieve Wikipedia article: {str(e)}",
                sources=[],
            )
