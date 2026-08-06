"""LiteLLM Gateway for provider-agnostic model access."""

import os
from typing import AsyncGenerator, List, Dict, Any, Optional
import litellm
from app.core.config import settings
from app.core.logging import logger

# Drop litellm internal logs unless debugging
if not settings.DEBUG:
    litellm.suppress_debug_info = True

class LLMGateway:
    """Singleton gateway wrapping LiteLLM for all AI interactions."""
    
    def __init__(self):
        self.model = settings.LLM_MODEL
        self.api_base = settings.LITELLM_API_BASE
        
        # Set keys in environment for LiteLLM to pick up automatically
        if settings.GOOGLE_API_KEY:
            os.environ["GEMINI_API_KEY"] = settings.GOOGLE_API_KEY
        if getattr(settings, "OPENAI_API_KEY", None):
            os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
        if getattr(settings, "ANTHROPIC_API_KEY", None):
            os.environ["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY
        if getattr(settings, "GROQ_API_KEY", None):
            os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY

        # LangSmith Tracing & Observability
        langsmith_key = getattr(settings, "LANGSMITH_API_KEY", None) or getattr(settings, "LANGCHAIN_API_KEY", None)
        if langsmith_key:
            os.environ["LANGSMITH_API_KEY"] = langsmith_key
            os.environ["LANGCHAIN_API_KEY"] = langsmith_key
            proj = getattr(settings, "LANGSMITH_PROJECT", None) or getattr(settings, "LANGCHAIN_PROJECT", None) or "Agentic RAG"
            os.environ["LANGSMITH_PROJECT"] = proj
            os.environ["LANGCHAIN_PROJECT"] = proj
            endpoint = getattr(settings, "LANGSMITH_ENDPOINT", None) or getattr(settings, "LANGCHAIN_ENDPOINT", None) or "https://api.smith.langchain.com"
            os.environ["LANGSMITH_ENDPOINT"] = endpoint
            os.environ["LANGCHAIN_ENDPOINT"] = endpoint
            os.environ["LANGSMITH_TRACING"] = "true"
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            if not hasattr(litellm, "success_callback") or litellm.success_callback is None:
                litellm.success_callback = []
            if "langsmith" not in litellm.success_callback:
                litellm.success_callback.append("langsmith")

    async def stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """Stream response tokens back."""
        try:
            response = await litellm.acompletion(
                model=self.model,
                messages=messages,
                api_base=self.api_base,
                stream=True,
                num_retries=3,
                fallbacks=["groq/llama3-8b-8192"],
                **kwargs
            )
            async for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            logger.error(f"LiteLLM streaming failed: {str(e)}")
            yield f"\n\n[Error: Model generation failed - {str(e)}]"

    async def complete(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Get a single string completion."""
        try:
            response = await litellm.acompletion(
                model=self.model,
                messages=messages,
                api_base=self.api_base,
                num_retries=3,
                fallbacks=["groq/llama3-8b-8192"],
                **kwargs
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"LiteLLM completion failed: {str(e)}")
            return ""

# Singleton instance
gateway = LLMGateway()
