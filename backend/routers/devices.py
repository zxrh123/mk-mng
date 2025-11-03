"""
??? Devices Router - ???? ????? ???????
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel, Field
from datetime import datetime

from database import get_db
from models import Device, DeviceStatus, User
from monitoring_engine import monitoring_engine

router = APIRouter()

# Schemas

class DeviceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    ip_address: str = Field(..., pattern=r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    port: int = Field(default=8728, ge=1, le=65535)
    ssh_port: int = Field(default=22, ge=1, le=65535)
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    model: str | None = None
    location: str | None = None
    description: str | None = None
    tags: List[str] = Field(default_factory=list)

class DeviceUpdate(BaseModel):
    name: str | None = None
    ip_address: str | None = None
    port: int | None = None
    ssh_port: int | None = None
    username: str | None = None
    password: str | None = None
    model: str | None = None
    location: str | None = None
    description: str | None = None
    tags: List[str] | None = None
    status: DeviceStatus | None = None

class DeviceResponse(BaseModel):
    id: int
    name: str
    ip_address: str
    port: int
    ssh_port: int
    username: str
    model: str | None
    routeros_version: str | None
    status: DeviceStatus
    location: str | None
    description: str | None
    tags: List[str]
    last_seen: datetime | None
    created_at: datetime
    updated_at: datetime | None
    
    class Config:
        from_attributes = True

# Routes

@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(
    device_data: DeviceCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    ????? ???? ????
    Create new device
    """
    # ?????? ?? ??? ???? ???? ???? IP
    result = await db.execute(
        select(Device).where(Device.ip_address == device_data.ip_address)
    )
    existing_device = result.scalar_one_or_none()
    
    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Device with IP {device_data.ip_address} already exists"
        )
    
    # ????? ??????
    device = Device(
        **device_data.model_dump(exclude={'password'}),
        encrypted_password=device_data.password,  # ??? ???????
        status=DeviceStatus.OFFLINE
    )
    
    db.add(device)
    await db.commit()
    await db.refresh(device)
    
    return device

@router.get("/", response_model=List[DeviceResponse])
async def list_devices(
    skip: int = 0,
    limit: int = 100,
    status_filter: DeviceStatus | None = None,
    db: AsyncSession = Depends(get_db)
):
    """
    ????? ???????
    List devices
    """
    query = select(Device)
    
    if status_filter:
        query = query.where(Device.status == status_filter)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    devices = result.scalars().all()
    
    return devices

@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    ?????? ??? ???? ????
    Get specific device
    """
    result = await db.execute(
        select(Device).where(Device.id == device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device {device_id} not found"
        )
    
    return device

@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: int,
    device_data: DeviceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    ????? ????
    Update device
    """
    result = await db.execute(
        select(Device).where(Device.id == device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device {device_id} not found"
        )
    
    # ????? ??????
    update_data = device_data.model_dump(exclude_unset=True)
    
    if 'password' in update_data:
        update_data['encrypted_password'] = update_data.pop('password')
    
    for field, value in update_data.items():
        setattr(device, field, value)
    
    await db.commit()
    await db.refresh(device)
    
    return device

@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    ??? ????
    Delete device
    """
    result = await db.execute(
        select(Device).where(Device.id == device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device {device_id} not found"
        )
    
    await db.delete(device)
    await db.commit()
    
    return None

@router.get("/{device_id}/health")
async def get_device_health(
    device_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    ?????? ??? ??? ??????
    Get device health
    """
    health = await monitoring_engine.get_device_health(db, device_id)
    return health

@router.post("/{device_id}/test-connection")
async def test_device_connection(
    device_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    ?????? ??????? ???????
    Test device connection
    """
    from mikrotik_connector import connection_pool
    
    result = await db.execute(
        select(Device).where(Device.id == device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device {device_id} not found"
        )
    
    connector = await connection_pool.get_connector(
        device_id=device.id,
        host=device.ip_address,
        username=device.username,
        password=device.encrypted_password,
        port=device.ssh_port
    )
    
    connected = await connector.connect()
    
    if connected:
        # ?????? ??? ??????? ??????
        resources = await connector.get_system_resources()
        await connector.disconnect()
        
        return {
            "success": True,
            "message": "????? ????",
            "device_info": resources
        }
    else:
        return {
            "success": False,
            "message": "??? ???????"
        }

@router.get("/{device_id}/metrics")
async def get_device_metrics(
    device_id: int,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    ?????? ??? ?????? ??????
    Get device metrics
    """
    from models import DeviceMetric
    
    result = await db.execute(
        select(DeviceMetric)
        .where(DeviceMetric.device_id == device_id)
        .order_by(DeviceMetric.collected_at.desc())
        .limit(limit)
    )
    metrics = result.scalars().all()
    
    return [
        {
            "cpu_load": m.cpu_load,
            "memory_used": m.memory_used,
            "active_users": m.active_users,
            "latency": m.latency,
            "packet_loss": m.packet_loss,
            "collected_at": m.collected_at.isoformat()
        }
        for m in metrics
    ]

@router.get("/{device_id}/interfaces")
async def get_device_interfaces(
    device_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    ?????? ??? ?????? ??????
    Get device interfaces
    """
    from models import Interface
    
    result = await db.execute(
        select(Interface).where(Interface.device_id == device_id)
    )
    interfaces = result.scalars().all()
    
    return interfaces

@router.get("/{device_id}/alerts")
async def get_device_alerts(
    device_id: int,
    resolved: bool | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    ?????? ??? ??????? ??????
    Get device alerts
    """
    from models import Alert
    
    query = select(Alert).where(Alert.device_id == device_id)
    
    if resolved is not None:
        query = query.where(Alert.is_resolved == resolved)
    
    query = query.order_by(Alert.created_at.desc()).limit(limit)
    
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    return alerts
