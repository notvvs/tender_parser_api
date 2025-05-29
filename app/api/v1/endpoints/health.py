from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Any

from app.schemas.api import HealthCheckResponse
from app.repository.database import repository, task_repository
from app.services.task_manager import get_task_manager

router = APIRouter()

# Время запуска сервиса
startup_time = datetime.now()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """Проверка здоровья сервиса"""
    # Проверка MongoDB для тендеров
    mongodb_status = "error"
    try:
        await repository.collection.find_one({}, {"_id": 1})
        # Также проверяем коллекцию задач
        await task_repository.collection.find_one({}, {"_id": 1})
        mongodb_status = "ok"
    except Exception as e:
        mongodb_status = f"error: {str(e)}"

    # Упрощенная проверка Playwright - просто проверяем, что можем создать браузер
    playwright_status = "error"
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            # Просто пробуем запустить браузер
            browser = await p.chromium.launch(
                headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            await browser.close()
            playwright_status = "ok"

    except Exception as e:
        playwright_status = f"error: {str(e)}"

    # Количество активных задач
    task_manager = get_task_manager()
    tasks_count = await task_manager.get_active_tasks_count()

    # Время работы
    uptime = (datetime.now() - startup_time).total_seconds()

    # Общий статус
    overall_status = "healthy" if mongodb_status == "ok" else "degraded"

    return HealthCheckResponse(
        status=overall_status,
        mongodb=mongodb_status,
        playwright=playwright_status,
        tasks_in_memory=tasks_count,
        uptime_seconds=uptime,
    )


@router.get("/ping")
async def ping() -> Dict[str, str]:
    """Простая проверка доступности"""
    return {"status": "pong"}


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    """Получение статистики по задачам"""
    task_manager = get_task_manager()
    stats = await task_manager.get_stats()

    return {
        "tasks": stats,
        "uptime_seconds": (datetime.now() - startup_time).total_seconds(),
        "timestamp": datetime.now(),
    }
