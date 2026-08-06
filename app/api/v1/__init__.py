from fastapi import APIRouter
from app.api.v1.chat import router as chat_router
from app.api.v1.health import router as health_router
from app.api.v1.voice import router as voice_router
from app.api.v1.eval import router as eval_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(voice_router)
api_v1_router.include_router(eval_router)

