from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from app.core.auth import verify_api_key
from app.schemas.api import (
    CreateTaskRequest,
    TaskResponse,
    TaskResult
)
from app.services.task_manager import get_task_manager
from app.utils.validator import validate_tender_url

router = APIRouter()


@router.post("/parse", response_model=TaskResponse, dependencies=[Depends(verify_api_key)])
async def create_parse_task(request: CreateTaskRequest) -> TaskResponse:
    """
    Создает задачу парсинга тендера

    - **url**: URL страницы тендера на zakupki.gov.ru
    """
    is_valid, error_message = validate_tender_url(str(request.url))
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)

    task_manager = get_task_manager()

    task_id = await task_manager.create_task(
        url=str(request.url),
    )

    status = await task_manager.get_task_status(task_id)
    return status


@router.get("/task/{task_id}/status", response_model=TaskResponse, dependencies=[Depends(verify_api_key)])
async def get_task_status(task_id: str) -> TaskResponse:
    """
    Получает статус задачи по ID

    - **task_id**: Идентификатор задачи
    """
    task_manager = get_task_manager()
    status = await task_manager.get_task_status(task_id)

    if not status:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    return status


@router.get("/task/{task_id}/result", response_model=TaskResult, dependencies=[Depends(verify_api_key)])
async def get_task_result(task_id: str) -> TaskResult:
    """
    Получает результат выполнения задачи

    - **task_id**: Идентификатор задачи

    Возвращает полные данные о тендере, если задача выполнена успешно
    """
    task_manager = get_task_manager()
    result = await task_manager.get_task_result(task_id)

    if not result:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    return result


@router.delete("/task/{task_id}", dependencies=[Depends(verify_api_key)])
async def delete_task(task_id: str) -> Dict[str, str]:
    """Удаляет задачу из памяти"""
    task_manager = get_task_manager()

    async with task_manager.lock:
        if task_id in task_manager.tasks:
            del task_manager.tasks[task_id]
            return {"message": "Задача удалена"}
        else:
            raise HTTPException(status_code=404, detail="Задача не найдена")


@router.post("/cleanup", dependencies=[Depends(verify_api_key)])
async def cleanup_tasks(hours: int = 24) -> Dict[str, str]:
    """
    Очищает старые задачи из памяти

    - **hours**: Возраст задач в часах для удаления (по умолчанию 24)
    """
    task_manager = get_task_manager()
    await task_manager.cleanup_old_tasks(hours)
    return {"message": f"Очистка задач старше {hours} часов выполнена"}