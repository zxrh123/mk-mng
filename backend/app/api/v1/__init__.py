"""
API v1 Router
"""

from fastapi import APIRouter
from app.api.v1 import routers, chat, monitoring, execution

router = APIRouter()

router.include_router(routers.router, prefix="/routers", tags=["routers"])
router.include_router(chat.router, prefix="/chat", tags=["chat"])
router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
router.include_router(execution.router, prefix="/execution", tags=["execution"])
