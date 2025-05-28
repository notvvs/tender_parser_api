import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime
from uuid import uuid4
import traceback

from app.core.settings import settings
from app.schemas.api import TaskStatus, TaskResponse, TaskResult
from app.parsers.all_tender_info import get_tender
from app.repository.database import repository

logger = logging.getLogger(__name__)

# Глобальный экземпляр
_task_manager_instance: Optional['TaskManager'] = None


def get_task_manager() -> 'TaskManager':
    """Получить экземпляр менеджера задач (Singleton)"""
    global _task_manager_instance
    if _task_manager_instance is None:
        _task_manager_instance = TaskManager()
    return _task_manager_instance

class TaskManager:
    """Менеджер для управления задачами парсинга"""

    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self.lock = asyncio.Lock()
        self.semaphore = asyncio.Semaphore(settings.max_concurrent_tasks)

    async def create_task(self, url: str, metadata: Optional[Dict] = None) -> str:
        """Создает новую задачу и запускает ее в фоне"""
        task_id = str(uuid4())

        # Создаем запись о задаче
        task_data = {
            "task_id": task_id,
            "url": url,
            "status": TaskStatus.PENDING,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "metadata": metadata,
            "result": None,
            "error": None,
            "completed_at": None
        }

        async with self.lock:
            self.tasks[task_id] = task_data

        # Запускаем парсинг в фоне
        asyncio.create_task(self._process_task(task_id))

        logger.info(f"Создана задача {task_id} для URL: {url}")
        return task_id

    async def _process_task(self, task_id: str):
        """Обработка задачи парсинга"""
        start_time = datetime.now()

        try:
            # Обновляем статус
            await self._update_task_status(task_id, TaskStatus.PROCESSING)

            # Получаем данные задачи
            task_data = self.tasks[task_id]
            url = task_data["url"]

            logger.info(f"Начало обработки задачи {task_id}")

            # Парсинг
            tender_data = await get_tender(url)

            # Сохранение в БД
            tender_id = await repository.save(tender_data.model_dump())

            # Сохраняем результат
            result = {
                "tender_id": tender_id,
                "tender_number": tender_data.tenderInfo.tenderNumber,
                "items_count": len(tender_data.items),
                "documents_count": len(tender_data.attachments),
                "data": tender_data.model_dump()
            }

            # Обновляем задачу
            async with self.lock:
                self.tasks[task_id].update({
                    "status": TaskStatus.COMPLETED,
                    "result": result,
                    "completed_at": datetime.now(),
                    "updated_at": datetime.now(),
                    "processing_time": (datetime.now() - start_time).total_seconds()
                })

            logger.info(
                f"Задача {task_id} успешно завершена за {(datetime.now() - start_time).total_seconds():.2f} сек")

        except Exception as e:
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            logger.error(f"Ошибка в задаче {task_id}: {error_msg}")

            async with self.lock:
                self.tasks[task_id].update({
                    "status": TaskStatus.FAILED,
                    "error": str(e),
                    "completed_at": datetime.now(),
                    "updated_at": datetime.now(),
                    "processing_time": (datetime.now() - start_time).total_seconds()
                })

    async def _update_task_status(self, task_id: str, status: TaskStatus):
        """Обновление статуса задачи"""
        async with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id]["status"] = status
                self.tasks[task_id]["updated_at"] = datetime.now()

    async def get_task_status(self, task_id: str) -> Optional[TaskResponse]:
        """Получение статуса задачи"""
        async with self.lock:
            if task_id not in self.tasks:
                return None

            task = self.tasks[task_id]
            return TaskResponse(
                task_id=task_id,
                status=task["status"],
                created_at=task["created_at"],
                updated_at=task["updated_at"],
                url=task["url"],
                error=task.get("error"),
                result_available=task["status"] == TaskStatus.COMPLETED
            )

    async def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Получение результата задачи"""
        async with self.lock:
            if task_id not in self.tasks:
                return None

            task = self.tasks[task_id]

            # Возвращаем только базовую информацию, если задача не завершена
            if task["status"] not in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                return TaskResult(
                    task_id=task_id,
                    status=task["status"],
                    created_at=task["created_at"],
                    error=task.get("error")
                )

            return TaskResult(
                task_id=task_id,
                status=task["status"],
                data=task.get("result", {}).get("data") if task["status"] == TaskStatus.COMPLETED else None,
                error=task.get("error"),
                created_at=task["created_at"],
                completed_at=task.get("completed_at"),
                processing_time=task.get("processing_time")
            )

    async def cleanup_old_tasks(self, hours: int = 24):
        """Очистка старых задач из памяти"""
        current_time = datetime.now()

        async with self.lock:
            tasks_to_remove = []

            for task_id, task in self.tasks.items():
                if task.get("completed_at"):
                    age = (current_time - task["completed_at"]).total_seconds() / 3600
                    if age > hours:
                        tasks_to_remove.append(task_id)

            for task_id in tasks_to_remove:
                del self.tasks[task_id]

            if tasks_to_remove:
                logger.info(f"Очищено {len(tasks_to_remove)} старых задач")