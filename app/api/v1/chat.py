"""Chat and SSE streaming API routes."""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService
from app.api.v1.deps import get_chat_service

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/stream")
async def chat_stream_endpoint(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Stream tokens and reasoning steps via Server-Sent Events (SSE).
    """
    return StreamingResponse(
        chat_service.stream_chat(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
