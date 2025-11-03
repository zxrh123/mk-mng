"""
Chat API - AI Chat Interface
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database.database import get_db
from app.database.models import ChatHistory
from app.core.ai_brain import AIBrain

router = APIRouter()
ai_brain = AIBrain()


class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    response: str
    execution_plan: Optional[dict] = None
    session_id: str


@router.post("/", response_model=ChatResponse)
async def chat(
    chat_message: ChatMessage,
    db: Session = Depends(get_db)
):
    """Chat with AI"""
    try:
        # Get AI response
        ai_response = await ai_brain.chat_response(
            chat_message.message,
            chat_message.context or {}
        )
        
        # Get execution plan
        execution_plan = await ai_brain.make_decision(
            chat_message.message,
            chat_message.context or {}
        )
        
        # Save to history
        session_id = chat_message.session_id or f"session_{db.query(ChatHistory).count() + 1}"
        chat_history = ChatHistory(
            session_id=session_id,
            user_message=chat_message.message,
            ai_response=ai_response,
            intent=execution_plan.get("intent"),
            execution_plan=execution_plan
        )
        db.add(chat_history)
        db.commit()
        
        return ChatResponse(
            response=ai_response,
            execution_plan=execution_plan,
            session_id=session_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    """Get chat history for session"""
    history = db.query(ChatHistory).filter(
        ChatHistory.session_id == session_id
    ).order_by(ChatHistory.created_at).all()
    
    return [
        {
            "user_message": h.user_message,
            "ai_response": h.ai_response,
            "created_at": h.created_at.isoformat()
        }
        for h in history
    ]
