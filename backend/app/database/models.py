"""
Database Models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base


class Router(Base):
    """MikroTik Router model"""
    __tablename__ = "routers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    host = Column(String(255), nullable=False)
    username = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    monitoring_data = relationship("MonitoringData", back_populates="router")
    executions = relationship("Execution", back_populates="router")


class MonitoringData(Base):
    """Monitoring data storage"""
    __tablename__ = "monitoring_data"
    
    id = Column(Integer, primary_key=True, index=True)
    router_id = Column(Integer, ForeignKey("routers.id"))
    cpu_load = Column(Float)
    ram_usage = Column(Float)
    disk_usage = Column(Float)
    interfaces_data = Column(JSON)
    hotspot_users_count = Column(Integer, default=0)
    latency = Column(Float)
    packet_loss = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    router = relationship("Router", back_populates="monitoring_data")


class Execution(Base):
    """Execution history"""
    __tablename__ = "executions"
    
    id = Column(Integer, primary_key=True, index=True)
    router_id = Column(Integer, ForeignKey("routers.id"))
    execution_id = Column(String(255), unique=True, index=True)
    script = Column(Text)
    status = Column(String(50))  # pending, completed, failed, rolled_back
    result = Column(JSON)
    error = Column(Text)
    dry_run = Column(Boolean, default=True)
    auto_execute = Column(Boolean, default=False)
    snapshot = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    router = relationship("Router", back_populates="executions")


class Alert(Base):
    """System alerts"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    router_id = Column(Integer, ForeignKey("routers.id"), nullable=True)
    alert_type = Column(String(100))  # high_cpu, interface_down, etc.
    severity = Column(String(50))  # info, warning, error, critical
    message = Column(Text)
    data = Column(JSON)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ChatHistory(Base):
    """Chat history with AI"""
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True)
    user_message = Column(Text)
    ai_response = Column(Text)
    intent = Column(JSON)
    execution_plan = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class KnowledgeBase(Base):
    """AI Knowledge Base"""
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(255), index=True)
    patterns = Column(JSON)
    solutions = Column(JSON)
    examples = Column(JSON)
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
