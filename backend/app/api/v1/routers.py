"""
Router Management API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.database.database import get_db
from app.database.models import Router

router = APIRouter()


class RouterCreate(BaseModel):
    name: str
    host: str
    username: str
    password: str
    description: str = None


class RouterResponse(BaseModel):
    id: int
    name: str
    host: str
    username: str
    description: str = None
    is_active: bool
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[RouterResponse])
async def get_routers(db: Session = Depends(get_db)):
    """Get all routers"""
    routers = db.query(Router).all()
    return routers


@router.get("/{router_id}", response_model=RouterResponse)
async def get_router(router_id: int, db: Session = Depends(get_db)):
    """Get router by ID"""
    router_obj = db.query(Router).filter(Router.id == router_id).first()
    if not router_obj:
        raise HTTPException(status_code=404, detail="Router not found")
    return router_obj


@router.post("/", response_model=RouterResponse)
async def create_router(router_data: RouterCreate, db: Session = Depends(get_db)):
    """Create new router"""
    router_obj = Router(**router_data.dict())
    db.add(router_obj)
    db.commit()
    db.refresh(router_obj)
    return router_obj


@router.put("/{router_id}", response_model=RouterResponse)
async def update_router(
    router_id: int,
    router_data: RouterCreate,
    db: Session = Depends(get_db)
):
    """Update router"""
    router_obj = db.query(Router).filter(Router.id == router_id).first()
    if not router_obj:
        raise HTTPException(status_code=404, detail="Router not found")
    
    for key, value in router_data.dict().items():
        setattr(router_obj, key, value)
    
    db.commit()
    db.refresh(router_obj)
    return router_obj


@router.delete("/{router_id}")
async def delete_router(router_id: int, db: Session = Depends(get_db)):
    """Delete router"""
    router_obj = db.query(Router).filter(Router.id == router_id).first()
    if not router_obj:
        raise HTTPException(status_code=404, detail="Router not found")
    
    db.delete(router_obj)
    db.commit()
    return {"message": "Router deleted successfully"}
