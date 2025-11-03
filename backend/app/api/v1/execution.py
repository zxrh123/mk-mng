"""
Execution API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database.database import get_db
from app.database.models import Router, Execution
from app.core.executor_engine import ExecutorEngine

router = APIRouter()
executor_engine = ExecutorEngine()


class ExecuteRequest(BaseModel):
    script: str
    dry_run: bool = True
    auto_execute: bool = False


class ExecuteResponse(BaseModel):
    execution_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None


@router.post("/routers/{router_id}/execute", response_model=ExecuteResponse)
async def execute_script(
    router_id: int,
    request: ExecuteRequest,
    db: Session = Depends(get_db)
):
    """Execute RouterOS script"""
    router = db.query(Router).filter(Router.id == router_id).first()
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")
    
    result = await executor_engine.execute_script(
        str(router_id),
        router.host,
        router.username,
        router.password,
        request.script,
        request.dry_run,
        request.auto_execute
    )
    
    # Save to database
    execution = Execution(
        router_id=router_id,
        execution_id=result["execution_id"],
        script=request.script,
        status=result["status"],
        result=result.get("result"),
        error=result.get("error"),
        dry_run=request.dry_run,
        auto_execute=request.auto_execute,
        snapshot=result.get("snapshot")
    )
    db.add(execution)
    db.commit()
    
    return ExecuteResponse(
        execution_id=result["execution_id"],
        status=result["status"],
        result=result.get("result"),
        error=result.get("error")
    )


@router.get("/routers/{router_id}/history")
async def get_execution_history(
    router_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get execution history"""
    router = db.query(Router).filter(Router.id == router_id).first()
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")
    
    executions = db.query(Execution).filter(
        Execution.router_id == router_id
    ).order_by(Execution.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": e.id,
            "execution_id": e.execution_id,
            "status": e.status,
            "script": e.script,
            "result": e.result,
            "error": e.error,
            "dry_run": e.dry_run,
            "created_at": e.created_at.isoformat()
        }
        for e in executions
    ]


@router.post("/routers/{router_id}/rollback")
async def rollback_execution(
    router_id: int,
    execution_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Rollback execution"""
    router = db.query(Router).filter(Router.id == router_id).first()
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")
    
    result = await executor_engine.rollback(
        str(router_id),
        router.host,
        router.username,
        router.password,
        execution_id
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result
