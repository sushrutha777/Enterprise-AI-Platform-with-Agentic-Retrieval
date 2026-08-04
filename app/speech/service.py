"""Speech Service Abstraction."""

from abc import ABC, abstractmethod
from typing import Optional
from google.cloud import speech
from app.core.config import settings
from app.core.logging import logger

class BaseSpeechService(ABC):
    """Abstract base class for Speech-to-Text providers."""
    
    @abstractmethod
    async def transcribe(self, audio_content: bytes) -> str:
        pass

class GCPSpeechService(BaseSpeechService):
    """Google Cloud Speech-to-Text implementation."""
    
    async def transcribe(self, audio_content: bytes) -> str:
        if not settings.GCP_STT_ENABLED:
            raise Exception("GCP Speech-to-Text is not enabled.")
            
        client = speech.SpeechAsyncClient()
        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code="en-US",
            enable_automatic_punctuation=True,
        )

        response = await client.recognize(config=config, audio=audio)
        transcript = " ".join([result.alternatives[0].transcript for result in response.results])
        return transcript.strip()

class SpeechService:
    """Factory and facade for the active Speech Service."""
    
    def __init__(self):
        # In the future, this could select provider based on settings (e.g. settings.SPEECH_PROVIDER)
        self.provider = GCPSpeechService()
        
    async def transcribe(self, audio_content: bytes) -> str:
        return await self.provider.transcribe(audio_content)

# Singleton instance
speech_service = SpeechService()
