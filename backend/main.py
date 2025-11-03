"""
?? Main FastAPI Application
??????? ??????? ??????
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from config import settings
from database import init_db, close_db, get_db
from monitoring_engine import monitoring_engine
from executor_engine import executor_engine
from core_ai_brain import ai_brain

# ????? ???? ???????
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ????? ???? ???? ???????
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    ????? ???? ???? ???????
    Application lifespan management
    """
    # ??? ???????
    logger.info("?? Starting MikroTik AI Management Platform...")
    
    # ????? ????? ????????
    await init_db()
    
    # ??? ???? ????????
    # await monitoring_engine.start(await get_db().__anext__())
    
    # ??? ???? ???????
    await executor_engine.start()
    
    logger.info("? Application started successfully!")
    
    yield
    
    # ????? ???????
    logger.info("? Shutting down...")
    
    # ????? ????????
    await monitoring_engine.stop()
    await executor_engine.stop()
    
    # ????? ????? ????????
    await close_db()
    
    logger.info("?? Application stopped")

# ????? ???????
app = FastAPI(
    title="MikroTik AI Management Platform",
    description="???? ???? ????? ??????? ?????? ????? MikroTik RouterOS",
    version="1.0.0",
    lifespan=lifespan
)

# ????? CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ???? ??????? WebSocket
class ConnectionManager:
    """
    ???? ??????? WebSocket
    WebSocket Connection Manager
    """
    
    def __init__(self):
        self.active_connections: dict = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket connected: {client_id}")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"WebSocket disconnected: {client_id}")
    
    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)

manager = ConnectionManager()

# Routes

@app.get("/")
async def root():
    """
    ???? ??????? ????????
    Root endpoint
    """
    return {
        "message": "?????? ?? ?? ???? ????? MikroTik ??????? ???????",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """
    ??? ??? ??????
    Health check
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "database": "connected",
            "ai_brain": "active",
            "monitoring_engine": "running" if monitoring_engine.is_running else "stopped",
            "executor_engine": "running" if executor_engine.is_running else "stopped"
        }
    }

@app.get("/api/v1/system/info")
async def system_info():
    """
    ??????? ??????
    System information
    """
    return {
        "name": "MikroTik AI Management Platform",
        "version": "1.0.0",
        "ai_models": {
            "primary": settings.OPENAI_MODEL,
            "secondary": settings.GEMINI_MODEL
        },
        "features": {
            "auto_execute": settings.AUTO_EXECUTE,
            "auto_heal": settings.ENABLE_AUTO_HEAL,
            "learning": settings.ENABLE_LEARNING
        },
        "monitoring": {
            "interval": settings.MONITORING_INTERVAL,
            "thresholds": {
                "cpu": settings.ALERT_THRESHOLD_CPU,
                "ram": settings.ALERT_THRESHOLD_RAM,
                "latency": settings.ALERT_THRESHOLD_LATENCY
            }
        }
    }

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    ???? ????? WebSocket ??????? ????
    WebSocket endpoint for real-time communication
    """
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # ??????? ????? ?? ??????
            data = await websocket.receive_json()
            
            # ?????? ???????
            message_type = data.get('type')
            
            if message_type == 'chat':
                # ????? ?????? ?? ?????? ???????
                user_message = data.get('message', '')
                
                # ????? ?????
                intent = await ai_brain.analyze_intent(user_message)
                
                # ????? ????
                await manager.send_personal_message({
                    "type": "chat_response",
                    "intent": intent,
                    "timestamp": datetime.now().isoformat()
                }, client_id)
            
            elif message_type == 'ping':
                # ?? ??? ping
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }, client_id)
            
            else:
                # ??? ????? ??? ?????
                await manager.send_personal_message({
                    "type": "error",
                    "error": f"Unknown message type: {message_type}",
                    "timestamp": datetime.now().isoformat()
                }, client_id)
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    ????? ??????? ?????
    Global exception handler
    """
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

# ????? ??? Routers (???? ??????? ??????)
# from routers import devices, tasks, chat, monitoring, auth
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
# app.include_router(devices.router, prefix="/api/v1/devices", tags=["Devices"])
# app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
# app.include_router(chat.router, prefix="/api/v1/chat", tags=["AI Chat"])
# app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["Monitoring"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
