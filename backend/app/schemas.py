from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
from app.models import QueueItemType, QueueItemStatus, TaskStatus

# Queue Option
class QueueOption(BaseModel):
    id: str
    label: str
    description: Optional[str] = None

# QueueItem schemas
class QueueItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    task_id: Optional[str] = None
    item_type: QueueItemType = QueueItemType.SINGLE_CHOICE
    options: Optional[List[QueueOption]] = None
    priority: int = 1
    source_agent: str = "ai_worker"

class QueueItemAnswer(BaseModel):
    selected_options: Optional[List[str]] = None  # IDs of selected options
    text_response: Optional[str] = None
    custom_data: Optional[Dict[str, Any]] = None

class QueueItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    task_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    item_type: QueueItemType
    options: Optional[List[Dict[str, Any]]] = None
    response_data: Optional[Dict[str, Any]] = None
    status: QueueItemStatus
    priority: int
    source_agent: str
    created_at: datetime
    resolved_at: Optional[datetime] = None

# Task schemas
class TaskCreate(BaseModel):
    title: Optional[str] = None
    prompt: str
    skills: List[str] = Field(default_factory=list)  # e.g. ["/web-search", "/code-analyzer"]
    schedule_cron: Optional[str] = None

class TaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    result_summary: Optional[str] = None

class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    prompt: str
    skills: List[str]
    schedule_cron: Optional[str] = None
    status: TaskStatus
    result_summary: Optional[str] = None
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    created_at: datetime

# Skill schemas
class SkillCreate(BaseModel):
    id: str
    name: str
    display_name: str
    description: str
    icon: str = "Globe"
    category: str = "general"
    parameters_schema: Optional[Dict[str, Any]] = None

class SkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    display_name: str
    description: str
    icon: str
    category: str
    parameters_schema: Optional[Dict[str, Any]] = None
