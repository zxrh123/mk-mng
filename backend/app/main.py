from __future__ import annotations

import json
from typing import Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api import api_router
from app.core.ai_brain import AIBrain
from app.core.ai_providers import AIIntegrationGateway
from app.core.config import settings
from app.core.logging import configure_logging  # noqa: F401
from app.db.session import AsyncSessionLocal, init_db
from app.services.executor import ExecutorEngine
from app.services.knowledge_base import KnowledgeBaseCrawler
from app.services.monitoring import MonitoringEngine


class ChatConnectionManager:
    def __init__(self) -> None:
        self.active_sessions: Dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_sessions[session_id] = websocket
        logger.info("WebSocket session {} connected", session_id)

    def disconnect(self, session_id: str) -> None:
        self.active_sessions.pop(session_id, None)
        logger.info("WebSocket session {} disconnected", session_id)

    async def send(self, session_id: str, message: Dict) -> None:
        websocket = self.active_sessions.get(session_id)
        if websocket:
            await websocket.send_json(message)


app = FastAPI(title=settings.project_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_str)

connection_manager = ChatConnectionManager()


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()
    ai_gateway = AIIntegrationGateway()
    monitoring = MonitoringEngine(AsyncSessionLocal)
    executor = ExecutorEngine(AsyncSessionLocal, ai_gateway)
    knowledge = KnowledgeBaseCrawler(AsyncSessionLocal, ai_gateway)
    brain = AIBrain(AsyncSessionLocal, ai_gateway, monitoring, executor, knowledge)
    await brain.startup()
    app.state.ai_brain = brain
    logger.info("Core AI Brain started")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    brain: AIBrain = app.state.ai_brain
    await brain.shutdown()


@app.websocket("/ws/assistant")
async def websocket_endpoint(websocket: WebSocket) -> None:
    session_id = websocket.query_params.get("session_id") or "websocket"
    await connection_manager.connect(session_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            message = payload.get("message", "")
            host = payload.get("host")
            brain: AIBrain = app.state.ai_brain
            response = await brain.handle_chat(session_id, message, host)
            await websocket.send_json(response)
    except WebSocketDisconnect:
        connection_manager.disconnect(session_id)
    except Exception as exc:  # noqa: BLE001
        logger.exception("WebSocket error: {}", exc)
        await websocket.close(code=1011, reason=str(exc))
        connection_manager.disconnect(session_id)


def get_app() -> FastAPI:
    return app
