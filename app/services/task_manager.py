import asyncio
import logging
from typing import Set, Optional
from datetime import datetime
from uuid import uuid4
import traceback

from app.core.settings import settings
from app.schemas.api import TaskStatus, TaskResponse, TaskResult
from app.parsers.all_tender_info import get_tender
from app.repository.database import repository, task_repository

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
        # Храним только ID активных задач для быстрой проверки
        self.active_tasks: Set[str] = set()
        self.lock = asyncio.Lock()
        self.semaphore = asyncio.Semaphore(settings.max_concurrent_tasks)
        self._initialized = False

    async def initialize(self):
        """Инициализация менеджера - загрузка активных задач из БД"""
        if self._initialized:
            return

        try:
            # Загружаем активные задачи из БД
            active_tasks = await task_repository.find_active_tasks()

            async with self.lock:
                for task in active_tasks:
                    self.active_tasks.add(task["task_id"])

                    # Перезапускаем обработку для задач в статусе PENDING
                    if task["status"] == TaskStatus.PENDING.value:
                        asyncio.create_task(self._process_task(task["task_id"]))
                        logger.info(f"Перезапущена обработка задачи {task['task_id']}")

            self._initialized = True
            logger.info(f"TaskManager инициализирован. Активных задач: {len(self.active_tasks)}")

        except Exception as e:
            logger.error(f"Ошибка при инициализации TaskManager: {e}")

    async def create_task(self, url: str, metadata: Optional[dict] = None) -> str:
        """Создает новую задачу и запускает ее в фоне"""
        # Убеждаемся что менеджер инициализирован
        await self.initialize()

        task_id = str(uuid4())

        # Создаем запись в БД
        task_data = {
            "task_id": task_id,
            "url": url,
            "status": TaskStatus.PENDING.value,
            "metadata": metadata,
            "result": None,
            "error": None,
            "processing_time": None
        }

        await task_repository.create_task(task_data)

        # Добавляем в активные задачи
        async with self.lock:
            self.active_tasks.add(task_id)

        # Запускаем парсинг в фоне
        asyncio.create_task(self._process_task(task_id))

        logger.info(f"Создана задача {task_id} для URL: {url}")
        return task_id

    async def _process_task(self, task_id: str):
        """Обработка задачи парсинга"""
        start_time = datetime.now()

        try:
            # Ограничиваем количество одновременных задач
            async with self.semaphore:
                # Обновляем статус в БД
                await task_repository.update_task_status(task_id, TaskStatus.PROCESSING)

                # Получаем данные задачи из БД
                task_data = await task_repository.find_by_task_id(task_id)
                if not task_data:
                    raise Exception(f"Задача {task_id} не найдена в БД")

                url = task_data["url"]
                logger.info(f"Начало обработки задачи {task_id}")

                # Парсинг
                tender_data = await get_tender(url)

                # Преобразуем в словарь и добавляем метаданные
                tender_dict = tender_data.model_dump()

                # Добавляем task_id и другие метаданные
                tender_dict['task_id'] = task_id
                tender_dict['parsed_at'] = datetime.now()
                tender_dict['source_url'] = url

                # Сохранение тендера в БД
                tender_id = await repository.save(tender_dict)

                # Подготавливаем результат
                result = {
                    "tender_id": tender_id,
                    "tender_number": tender_data.tenderInfo.tenderNumber,
                    "items_count": len(tender_data.items),
                    "documents_count": len(tender_data.attachments)
                }

                # Обновляем задачу в БД
                processing_time = (datetime.now() - start_time).total_seconds()
                await task_repository.complete_task(task_id, result, processing_time)

                logger.info(f"Задача {task_id} успешно завершена за {processing_time:.2f} сек")

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Ошибка в задаче {task_id}: {error_msg}\n{traceback.format_exc()}")

            # Обновляем статус в БД
            processing_time = (datetime.now() - start_time).total_seconds()
            await task_repository.fail_task(task_id, error_msg, processing_time)

        finally:
            # Удаляем из активных задач
            async with self.lock:
                self.active_tasks.discard(task_id)

    async def get_task_status(self, task_id: str) -> Optional[TaskResponse]:
        """Получение статуса задачи из БД"""
        task = await task_repository.find_by_task_id(task_id)

        if not task:
            return None

        return TaskResponse(
            task_id=task_id,
            status=TaskStatus(task["status"]),
            created_at=task["created_at"],
            updated_at=task["updated_at"],
            url=task["url"],
            error=task.get("error"),
            result_available=task["status"] == TaskStatus.COMPLETED.value
        )

    async def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Получение результата задачи из БД"""
        task = await task_repository.find_by_task_id(task_id)

        if not task:
            return None

        return TaskResult(
            task_id=task_id,
            status=TaskStatus(task["status"]),
            data=task.get("result"),  # Возвращаем только результат из коллекции tasks
            error=task.get("error"),
            created_at=task["created_at"],
            completed_at=task.get("completed_at"),
            processing_time=task.get("processing_time")
        )

    async def cleanup_old_tasks(self, hours: int = 24):
        """Очистка старых задач из БД"""
        deleted_count = await task_repository.delete_old_tasks(hours)
        logger.info(f"Очищено {deleted_count} старых задач")

    async def get_active_tasks_count(self) -> int:
        """Возвращает количество активных задач"""
        async with self.lock:
            return len(self.active_tasks)

    async def get_stats(self) -> dict:
        """Получает статистику по задачам"""
        stats = await task_repository.get_task_stats()
        stats["active_in_memory"] = await self.get_active_tasks_count()
        return stats