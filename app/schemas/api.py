from pydantic import BaseModel, HttpUrl, Field
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
    """Результат выполнения задачи"""
    task_id: str
    status: TaskStatus
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Краткая информация о результате: tender_id, tender_number, items_count, documents_count"
    )
    error: Optional[str] = Field(None, description="Текст ошибки (для проваленных задач)")
    created_at: datetime
    completed_at: Optional[datetime] = None
    processing_time: Optional[float] = Field(None, description="Время обработки в секундах")


class HealthCheckResponse(BaseModel):
    status: str
    mongodb: str
    playwright: str
    tasks_in_memory: int
    uptime_seconds: float