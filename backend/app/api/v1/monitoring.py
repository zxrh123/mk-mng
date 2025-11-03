"""
Monitoring API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.database.database import get_db
from app.database.models import Router, MonitoringData, Alert
from app.core.monitoring_engine import MonitoringEngine

router = APIRouter()
monitoring_engine = MonitoringEngine()


@router.get("/routers/{router_id}/status")
async def get_router_status(router_id: int, db: Session = Depends(get_db)):
    """Get current router status"""
    router = db.query(Router).filter(Router.id == router_id).first()
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")
    
    # Connect and get status
    connection = await monitoring_engine.connect_router(
        router.host,
        router.username,
        router.password
    )
    
    if not connection:
        raise HTTPException(status_code=500, detail="Failed to connect to router")
    
    resources = await monitoring_engine.get_system_resources(connection)
    interfaces = await monitoring_engine.get_interfaces_status(connection)
    hotspot_users = await monitoring_engine.get_hotspot_users(connection)
    latency = await monitoring_engine.check_latency(connection)
    
    return {
        "router_id": router_id,
        "resources": resources,
        "interfaces": interfaces,
        "hotspot_users": hotspot_users,
        "latency": latency,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/routers/{router_id}/history")
async def get_monitoring_history(
    router_id: int,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get monitoring history"""
    router = db.query(Router).filter(Router.id == router_id).first()
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")
    
    since = datetime.now() - timedelta(hours=hours)
    history = db.query(MonitoringData).filter(
        MonitoringData.router_id == router_id,
        MonitoringData.timestamp >= since
    ).order_by(MonitoringData.timestamp.desc()).all()
    
    return [
        {
            "id": h.id,
            "cpu_load": h.cpu_load,
            "ram_usage": h.ram_usage,
            "interfaces_data": h.interfaces_data,
            "hotspot_users_count": h.hotspot_users_count,
            "latency": h.latency,
            "timestamp": h.timestamp.isoformat()
        }
        for h in history
    ]


@router.get("/alerts")
async def get_alerts(
    router_id: Optional[int] = None,
    is_resolved: Optional[bool] = False,
    db: Session = Depends(get_db)
):
    """Get system alerts"""
    query = db.query(Alert)
    
    if router_id:
        query = query.filter(Alert.router_id == router_id)
    
    if is_resolved is not None:
        query = query.filter(Alert.is_resolved == is_resolved)
    
    alerts = query.order_by(Alert.created_at.desc()).limit(100).all()
    
    return [
        {
            "id": a.id,
            "router_id": a.router_id,
            "alert_type": a.alert_type,
            "severity": a.severity,
            "message": a.message,
            "data": a.data,
            "is_resolved": a.is_resolved,
            "created_at": a.created_at.isoformat()
        }
        for a in alerts
    ]


@router.post("/routers/{router_id}/start")
async def start_monitoring(router_id: int, db: Session = Depends(get_db)):
    """Start monitoring a router"""
    router = db.query(Router).filter(Router.id == router_id).first()
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")
    
    await monitoring_engine.start_monitoring(
        str(router_id),
        router.host,
        router.username,
        router.password
    )
    
    return {"message": "Monitoring started", "router_id": router_id}


@router.post("/routers/{router_id}/stop")
async def stop_monitoring(router_id: int):
    """Stop monitoring a router"""
    await monitoring_engine.stop_monitoring(str(router_id))
    return {"message": "Monitoring stopped", "router_id": router_id}
