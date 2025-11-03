from fastapi import Request

from app.core.ai_brain import AIBrain


def get_ai_brain(request: Request) -> AIBrain:
    brain: AIBrain = request.app.state.ai_brain
    return brain
