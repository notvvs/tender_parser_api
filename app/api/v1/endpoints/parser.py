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
from app.repository.database import repository, task_repository

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


@router.get("/task/{task_id}/result", dependencies=[Depends(verify_api_key)])
async def get_task_result(task_id: str) -> Dict[str, Any]:
    """
    Получает полные данные тендера по ID задачи

    - **task_id**: Идентификатор задачи

    Возвращает полный объект тендера из MongoDB со всеми позициями, документами и характеристиками
    """
    tender = await repository.find_by_task_id(task_id)

    if not tender:
        raise HTTPException(status_code=404, detail="Тендер не найден для данной задачи")

    # Преобразуем ObjectId в строку для JSON сериализации
    if "_id" in tender:
        tender["_id"] = str(tender["_id"])

    return tender


@router.delete("/task/{task_id}", dependencies=[Depends(verify_api_key)])
async def delete_task(task_id: str) -> Dict[str, str]:
    """
    Удаляет задачу из активных

    Примечание: Это удаляет task_id только из памяти (active_tasks).
    Данные в MongoDB остаются для истории.
    """
    task_manager = get_task_manager()

    async with task_manager.lock:
        if task_id in task_manager.active_tasks:
            task_manager.active_tasks.discard(task_id)
            return {"message": "Задача удалена из активных"}
        else:
            # Проверяем, есть ли задача в БД
            task = await task_repository.find_by_task_id(task_id)
            if task:
                return {"message": "Задача не активна (уже завершена или провалена)"}
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