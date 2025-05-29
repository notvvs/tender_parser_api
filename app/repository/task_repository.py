import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.schemas.api import TaskStatus

logger = logging.getLogger(__name__)


class TaskRepository:
    """Репозиторий для работы с задачами"""

    def __init__(self, db, collection_name: str = "tasks"):
        self.db = db
        self.collection = db[collection_name]

    async def create_task(self, task_data: Dict[str, Any]) -> str:
        """Создает новую задачу в БД"""
        task_data["created_at"] = datetime.now()
        task_data["updated_at"] = datetime.now()

        result = await self.collection.insert_one(task_data)
        logger.info(f"Создана задача в БД: {task_data['task_id']}")
        return str(result.inserted_id)

    async def update_task_status(self, task_id: str, status: TaskStatus, error: Optional[str] = None):
        """Обновляет статус задачи"""
        update_data = {
            "status": status.value,
            "updated_at": datetime.now()
        }

        if error:
            update_data["error"] = error

        if status == TaskStatus.PROCESSING:
            update_data["started_at"] = datetime.now()
        elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            update_data["completed_at"] = datetime.now()

        result = await self.collection.update_one(
            {"task_id": task_id},
            {"$set": update_data}
        )

        if result.modified_count > 0:
            logger.info(f"Обновлен статус задачи {task_id}: {status.value}")
        else:
            logger.warning(f"Задача {task_id} не найдена для обновления статуса")

    async def complete_task(self, task_id: str, result: Dict[str, Any], processing_time: float):
        """Завершает задачу с результатом"""
        update_data = {
            "status": TaskStatus.COMPLETED.value,
            "result": result,
            "completed_at": datetime.now(),
            "updated_at": datetime.now(),
            "processing_time": processing_time
        }

        await self.collection.update_one(
            {"task_id": task_id},
            {"$set": update_data}
        )
        logger.info(f"Задача {task_id} успешно завершена")

    async def fail_task(self, task_id: str, error: str, processing_time: float):
        """Помечает задачу как проваленную"""
        update_data = {
            "status": TaskStatus.FAILED.value,
            "error": error,
            "completed_at": datetime.now(),
            "updated_at": datetime.now(),
            "processing_time": processing_time
        }

        await self.collection.update_one(
            {"task_id": task_id},
            {"$set": update_data}
        )
        logger.error(f"Задача {task_id} завершилась с ошибкой: {error}")

    async def find_by_task_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Находит задачу по task_id"""
        result = await self.collection.find_one({"task_id": task_id})
        return result

    async def find_active_tasks(self) -> List[Dict[str, Any]]:
        """Находит все активные задачи (pending или processing)"""
        cursor = self.collection.find({
            "status": {"$in": [TaskStatus.PENDING.value, TaskStatus.PROCESSING.value]}
        })

        results = []
        async for document in cursor:
            results.append(document)
        return results

    async def delete_old_tasks(self, hours: int = 24) -> int:
        """Удаляет старые завершенные задачи"""
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(hours=hours)

        result = await self.collection.delete_many({
            "status": {"$in": [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value]},
            "completed_at": {"$lt": cutoff_date}
        })

        if result.deleted_count > 0:
            logger.info(f"Удалено {result.deleted_count} старых задач")

        return result.deleted_count

    async def get_task_stats(self) -> Dict[str, int]:
        """Получает статистику по задачам"""
        pipeline = [
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]

        stats = {}
        async for doc in self.collection.aggregate(pipeline):
            stats[doc["_id"]] = doc["count"]

        return stats