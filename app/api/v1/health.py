"""Health check and system telemetry API route."""

import os
import psutil
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    """General health check endpoint."""
    has_llm = bool(settings.LITELLM_API_BASE or settings.GOOGLE_API_KEY or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "gemini_configured": has_llm,
    }

@router.get("/health/live")
def liveness_check():
    """Kubernetes liveness probe."""
    return {"status": "alive"}

@router.get("/health/ready")
def readiness_check():
    """Kubernetes readiness probe."""
    # Check essential configs
    has_llm = bool(settings.LITELLM_API_BASE or settings.GOOGLE_API_KEY or os.getenv("GEMINI_API_KEY"))
    if not has_llm:
        return {"status": "not_ready", "reason": "Missing LLM configuration"}
    return {"status": "ready"}

@router.get("/health/metrics")
def metrics():
    """Basic performance and resource metrics."""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return {
        "memory_rss_mb": memory_info.rss / 1024 / 1024,
        "cpu_percent": process.cpu_percent(),
        "threads": process.num_threads(),
        "version": settings.VERSION,
    }
