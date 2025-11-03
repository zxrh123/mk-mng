from fastapi import APIRouter, Depends

from app.api.dependencies import get_ai_brain
from app.core.ai_brain import AIBrain
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse


router = APIRouter()


@router.post("/message", response_model=ChatMessageResponse)
async def chat_message(payload: ChatMessageRequest, brain: AIBrain = Depends(get_ai_brain)) -> ChatMessageResponse:
    response = await brain.handle_chat(payload.session_id, payload.message, payload.host)
    return ChatMessageResponse(message=response["message"], metadata=response.get("metadata", {}))
