from fastapi import APIRouter, Depends

from app.api.dependencies import get_ai_brain
from app.core.ai_brain import AIBrain
from app.schemas.automation import AutomationRequest, AutomationResponse


router = APIRouter()


@router.post("/execute", response_model=AutomationResponse)
async def execute_automation(payload: AutomationRequest, brain: AIBrain = Depends(get_ai_brain)) -> AutomationResponse:
    result = await brain.execute_objective(
        host=payload.host,
        objective=payload.objective,
        auto_execute=payload.auto_execute,
        session_id="automation-api",
    )
    return AutomationResponse(
        message="\u062a\u0645\u062a \u0645\u0639\u0627\u0644\u062c\u0629 \u0627\u0644\u0623\u0645\u0631 \u0628\u0646\u062c\u0627\u062d.",
        executed=result.get("executed", False),
        result=result,
    )
