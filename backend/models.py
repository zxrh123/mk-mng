from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class DeviceStatus(str, enum.Enum):
    """???? ??????"""
    ONLINE = "online"
    OFFLINE = "offline"
    WARNING = "warning"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class TaskStatus(str, enum.Enum):
    """???? ??????"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AlertSeverity(str, enum.Enum):
    """????? ????? ???????"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class User(Base):
    """
    ????? ????????
    User Model
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(String, default="user")  # admin, technician, user
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    devices = relationship("Device", back_populates="owner")
    tasks = relationship("Task", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")

class Device(Base):
    """
    ????? ???? MikroTik
    MikroTik Device Model
    """
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    ip_address = Column(String, unique=True, index=True, nullable=False)
    port = Column(Integer, default=8728)
    ssh_port = Column(Integer, default=22)
    username = Column(String, nullable=False)
    encrypted_password = Column(String, nullable=False)
    model = Column(String)
    routeros_version = Column(String)
    status = Column(Enum(DeviceStatus), default=DeviceStatus.OFFLINE)
    location = Column(String)
    description = Column(Text)
    tags = Column(JSON, default=[])
    config_snapshot = Column(JSON)
    last_seen = Column(DateTime(timezone=True))
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    owner = relationship("User", back_populates="devices")
    metrics = relationship("DeviceMetric", back_populates="device", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="device")
    alerts = relationship("Alert", back_populates="device", cascade="all, delete-orphan")
    interfaces = relationship("Interface", back_populates="device", cascade="all, delete-orphan")

class DeviceMetric(Base):
    """
    ?????? ???? ??????
    Device Performance Metrics
    """
    __tablename__ = "device_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    cpu_load = Column(Float)
    memory_used = Column(Float)
    memory_total = Column(Float)
    disk_used = Column(Float)
    disk_total = Column(Float)
    uptime = Column(String)
    active_users = Column(Integer, default=0)
    total_bandwidth_in = Column(Float)
    total_bandwidth_out = Column(Float)
    latency = Column(Float)
    packet_loss = Column(Float)
    temperature = Column(Float)
    voltage = Column(Float)
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    device = relationship("Device", back_populates="metrics")

class Interface(Base):
    """
    ?????? ?????? ??????
    Network Interfaces
    """
    __tablename__ = "interfaces"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String)  # ether, wlan, pppoe, etc.
    mac_address = Column(String)
    status = Column(String)  # running, disabled
    rx_bytes = Column(Float)
    tx_bytes = Column(Float)
    rx_packets = Column(Float)
    tx_packets = Column(Float)
    rx_errors = Column(Integer)
    tx_errors = Column(Integer)
    speed = Column(String)
    last_link_up_time = Column(String)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    device = relationship("Device", back_populates="interfaces")

class Task(Base):
    """
    ???? ??????
    System Tasks
    """
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))
    task_type = Column(String, nullable=False)  # config, monitor, diagnose, execute
    description = Column(Text)
    command = Column(Text)
    script = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    result = Column(JSON)
    error_message = Column(Text)
    dry_run = Column(Boolean, default=True)
    auto_execute = Column(Boolean, default=False)
    created_by_ai = Column(Boolean, default=False)
    ai_confidence = Column(Float)
    rollback_script = Column(Text)
    executed_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    user = relationship("User", back_populates="tasks")
    device = relationship("Device", back_populates="tasks")

class Alert(Base):
    """
    ??????? ??????
    System Alerts
    """
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.INFO)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    alert_type = Column(String)  # performance, security, connectivity, system
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True))
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    device = relationship("Device", back_populates="alerts")

class ChatSession(Base):
    """
    ????? ???????? ?? ?????? ???????
    AI Chat Sessions
    """
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String, unique=True, index=True, nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    context = Column(JSON)  # ???? ????????
    is_hotspot = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    
    # Relations
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    """
    ????? ????????
    Chat Messages
    """
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    ai_model = Column(String)  # gpt-4, gemini-pro
    intent = Column(String)  # detected intent
    confidence = Column(Float)
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    session = relationship("ChatSession", back_populates="messages")

class KnowledgeBase(Base):
    """
    ????? ???????
    Knowledge Base
    """
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)  # command, troubleshooting, best-practice
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String)  # mikrotik-forum, documentation, learned
    routeros_version = Column(String)
    tags = Column(JSON, default=[])
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float)
    embedding = Column(JSON)  # ????? ???????
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SystemLog(Base):
    """
    ????? ??????
    System Logs
    """
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String, index=True)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    module = Column(String, index=True)
    message = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
