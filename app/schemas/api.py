from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CreateTaskRequest(BaseModel):
    url: HttpUrl


class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    url: str
    error: Optional[str] = None
    result_available: bool = False


class TaskResult(BaseModel):
    task_id: str
    status: TaskStatus
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    processing_time: Optional[float] = None


class HealthCheckResponse(BaseModel):
    status: str
    mongodb: str
    playwright: str
    tasks_in_memory: int
    uptime_seconds: float