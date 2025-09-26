"""
Data models for the Multi-Agent Orchestration Platform
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
import uuid

Base = declarative_base()

class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AgentStatus(str, Enum):
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"

class MessageType(str, Enum):
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    COLLABORATION = "collaboration"
    STATUS_UPDATE = "status_update"
    ERROR = "error"

# SQLAlchemy Models
class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, default=AgentStatus.IDLE)
    capabilities = Column(JSON)
    current_load = Column(Integer, default=0)
    max_concurrent_tasks = Column(Integer, default=3)
    priority_weight = Column(Float, default=1.0)
    performance_score = Column(Float, default=1.0)
    total_tasks_completed = Column(Integer, default=0)
    average_completion_time = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    assigned_tasks = relationship("Task", back_populates="assigned_agent")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    task_type = Column(String, nullable=False)
    required_capabilities = Column(JSON)
    priority = Column(Integer, default=1)
    status = Column(String, default=TaskStatus.PENDING)
    assigned_agent_id = Column(String, ForeignKey("agents.id"), nullable=True)
    result = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    progress_percentage = Column(Float, default=0.0)
    estimated_duration = Column(Float, nullable=True)
    actual_duration = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    assigned_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)
    
    # Parent-child relationship for task decomposition
    parent_task_id = Column(String, ForeignKey("tasks.id"), nullable=True)
    parent_task = relationship("Task", remote_side="Task.id", back_populates="subtasks")
    subtasks = relationship("Task", back_populates="parent_task")
    
    # Relationships
    assigned_agent = relationship("Agent", back_populates="assigned_tasks")
    messages = relationship("Message", back_populates="task")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = Column(String, ForeignKey("agents.id"), nullable=False)
    receiver_id = Column(String, ForeignKey("agents.id"), nullable=True)  # Null for broadcast
    task_id = Column(String, ForeignKey("tasks.id"), nullable=True)
    message_type = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    
    # Relationships
    sender = relationship("Agent", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("Agent", foreign_keys=[receiver_id], back_populates="received_messages")
    task = relationship("Task", back_populates="messages")

class SystemMetrics(Base):
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    active_agents = Column(Integer, default=0)
    pending_tasks = Column(Integer, default=0)
    in_progress_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    failed_tasks = Column(Integer, default=0)
    average_response_time = Column(Float, default=0.0)
    system_load = Column(Float, default=0.0)
    throughput = Column(Float, default=0.0)

# Pydantic Models for API
class AgentCreate(BaseModel):
    agent_type: str
    name: str
    capabilities: List[str]
    max_concurrent_tasks: int = 3
    priority_weight: float = 1.0

class AgentResponse(BaseModel):
    id: str
    agent_type: str
    name: str
    status: AgentStatus
    capabilities: List[str]
    current_load: int
    max_concurrent_tasks: int
    priority_weight: float
    performance_score: float
    total_tasks_completed: int
    average_completion_time: float
    created_at: datetime
    last_active: datetime

class TaskCreate(BaseModel):
    title: str
    description: str
    task_type: str
    required_capabilities: List[str]
    priority: int = 1
    deadline: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    task_type: str
    required_capabilities: List[str]
    priority: int
    status: TaskStatus
    assigned_agent_id: Optional[str]
    result: Optional[str]
    error_message: Optional[str]
    progress_percentage: float
    estimated_duration: Optional[float]
    actual_duration: Optional[float]
    created_at: datetime
    assigned_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    deadline: Optional[datetime]

class MessageCreate(BaseModel):
    sender_id: str
    receiver_id: Optional[str] = None
    task_id: Optional[str] = None
    message_type: MessageType
    content: str
    message_metadata: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    id: str
    sender_id: str
    receiver_id: Optional[str]
    task_id: Optional[str]
    message_type: MessageType
    content: str
    message_metadata: Optional[Dict[str, Any]]
    timestamp: datetime
    is_read: bool

class SystemMetricsResponse(BaseModel):
    timestamp: datetime
    active_agents: int
    pending_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    failed_tasks: int
    average_response_time: float
    system_load: float
    throughput: float

class TaskAssignmentRequest(BaseModel):
    task_id: str
    preferred_agent_type: Optional[str] = None
    force_assignment: bool = False

class CollaborationRequest(BaseModel):
    task_id: str
    requesting_agent_id: str
    required_capabilities: List[str]
    collaboration_type: str  # "assistance", "review", "consensus"
    message: str
