"""
AI-Powered MikroTik Network Management Platform
Backend Main Entry Point
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv
import os

from app.core.config import settings
from app.api.v1 import router as api_router
from app.core.ai_brain import AIBrain
from app.core.websocket_manager import WebSocketManager
from app.database.database import engine, Base

load_dotenv()

# Initialize AI Brain globally
ai_brain = AIBrain()
websocket_manager = WebSocketManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events"""
    # Startup
    print("?? Starting AI-Powered MikroTik Management Platform...")
    await ai_brain.initialize()
    print("? AI Brain initialized")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("? Database initialized")
    
    yield
    
    # Shutdown
    print("?? Shutting down...")


app = FastAPI(
    title="AI MikroTik Management Platform",
    description="???? ???? ????? ??????? ?????? ????? MikroTik",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "AI-Powered MikroTik Management Platform",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ai_brain": ai_brain.is_ready(),
        "database": "connected"
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await websocket_manager.handle_message(websocket, data, ai_brain)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
