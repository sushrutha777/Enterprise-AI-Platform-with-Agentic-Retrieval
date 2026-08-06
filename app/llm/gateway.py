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
