"""AI command endpoints and WebSocket handler."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from pydantic import BaseModel

from app.ai.brain.orchestrator import ai_brain
from app.schema.ai import AICommandRequest, AICommandResponse, AIScript
from app.services.executor_engine import executor_engine
from app.storage.database import db
from app.models.router_event import AIDecision

router = APIRouter()


class ExecuteDecisionRequest(BaseModel):
    decision_id: UUID
    metadata: dict[str, str] | None = None


@router.post("/command", response_model=AICommandResponse)
async def handle_ai_command(request: AICommandRequest) -> AICommandResponse:
    return await ai_brain.handle_command(request)


@router.post("/decision/execute")
async def execute_decision(payload: ExecuteDecisionRequest) -> dict[str, str]:
    async with db.session() as session:
        decision = await session.get(AIDecision, payload.decision_id)

    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    if not decision.script:
        raise HTTPException(status_code=400, detail="Decision has no executable script")

    script = AIScript(contents=decision.script)
    result = await executor_engine.execute(decision.id, script, metadata=payload.metadata or {})
    return {"status": "executed", "decision_id": result.decision_id}


class AIWebSocketManager:
    """Lightweight websocket manager for AI chat streaming."""

    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        if websocket.application_state != WebSocketState.DISCONNECTED:
            await websocket.close()
        self._connections.discard(websocket)

    async def send(self, websocket: WebSocket, message: dict[str, str]) -> None:
        await websocket.send_json(message)


ws_manager = AIWebSocketManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            request = AICommandRequest(**data)
            response = await ai_brain.handle_command(request)
            await ws_manager.send(websocket, response.model_dump())
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)

