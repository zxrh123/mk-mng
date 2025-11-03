"""
WebSocket Manager for real-time communication
"""

from fastapi import WebSocket
from typing import List, Dict
import json
import asyncio


class WebSocketManager:
    """Manages WebSocket connections for real-time chat and notifications"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_sessions: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting: {e}")
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)
    
    async def handle_message(
        self, 
        websocket: WebSocket, 
        data: dict,
        ai_brain
    ):
        """Handle incoming WebSocket message"""
        message_type = data.get("type")
        
        if message_type == "chat":
            # Handle chat message
            user_message = data.get("message", "")
            context = data.get("context", {})
            
            # Get AI response
            chat_response = await ai_brain.chat_response(user_message, context)
            
            # Get execution plan if needed
            execution_plan = await ai_brain.make_decision(user_message, context)
            
            await self.send_personal_message({
                "type": "chat_response",
                "message": chat_response,
                "execution_plan": execution_plan,
                "timestamp": asyncio.get_event_loop().time()
            }, websocket)
        
        elif message_type == "execute":
            # Handle execution request
            execution_id = data.get("execution_id")
            confirm = data.get("confirm", False)
            
            await self.send_personal_message({
                "type": "execution_status",
                "execution_id": execution_id,
                "status": "processing",
                "message": "???? ???????..."
            }, websocket)
        
        elif message_type == "monitoring":
            # Handle monitoring request
            await self.send_personal_message({
                "type": "monitoring_data",
                "data": {}  # Will be filled by monitoring engine
            }, websocket)
