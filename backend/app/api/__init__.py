from fastapi import APIRouter

from .routes import automation, chat, health, monitoring


api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(automation.router, prefix="/automation", tags=["automation"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
