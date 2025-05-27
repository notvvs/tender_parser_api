import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


logger = logging.getLogger(__name__)

class BaseRepository(ABC):
    """Абстрактный базовый класс репозитория"""

    @abstractmethod
    async def save(self, data: Dict[str, Any]) -> str:
        """Сохраняет данные в БД"""
        pass

    @abstractmethod
    async def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Находит запись по ID"""
        pass

    @abstractmethod
    async def find_by_field(self, field: str, value: Any) -> Optional[Dict[str, Any]]:
        """Находит запись по указанному полю"""
        pass

    @abstractmethod
    async def find_all(self) -> List[Dict[str, Any]]:
        """Возвращает все записи"""
        pass

    @abstractmethod
    async def update(self, id: str, data: Dict[str, Any]) -> bool:
        """Обновляет запись по ID"""
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Удаляет запись по ID"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Закрывает соединение с БД"""
        pass


class TenderRepository(BaseRepository):
    """Репозиторий для работы с тендерами"""

    def __init__(self, db, collection_name: str = "tenders"):
        self.db = db
        self.collection = db[collection_name]

    async def save(self, data: Dict[str, Any]) -> str:
        """
        Сохраняет тендер в БД. Если тендер с таким номером уже существует,
        обновляет его данные.
        """
        tender_number = data["tenderInfo"]["tenderNumber"]

        # Проверяем существует ли тендер с таким номером
        existing_tender = await self.collection.find_one({"tenderInfo.tenderNumber": tender_number})

        if existing_tender:
            # Обновляем существующий тендер
            await self.collection.update_one(
                {"tenderInfo.tenderNumber": tender_number},
                {"$set": data}
            )
            logger.info(f"Обновлен существующий тендер: {tender_number}")
            return str(existing_tender["_id"])
        else:
            result = await self.collection.insert_one(data)
            logger.info(f"Создан новый тендер: {tender_number}")
            return str(result.inserted_id)

    async def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Находит тендер по ID"""
        try:
            result = await self.collection.find_one({"_id": id})
            return result
        except Exception as e:
            logger.error(f"Ошибка при поиске по ID: {e}")
            return None

    async def find_by_field(self, field: str, value: Any) -> Optional[Dict[str, Any]]:
        """Находит тендер по указанному полю"""
        result = await self.collection.find_one({field: value})
        return result


    async def find_by_tender_number(self, tender_number: str) -> Optional[Dict[str, Any]]:
        """Находит тендер по номеру"""
        return await self.find_by_field("tenderInfo.tenderNumber", tender_number)


    async def find_all(self, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """Возвращает все тендеры с пагинацией"""
        cursor = self.collection.find({}).skip(skip).limit(limit).sort("parsed_at", -1)
        results = []
        async for document in cursor:
            results.append(document)
        return results

    async def update(self, id: str, data: Dict[str, Any]) -> bool:
        """Обновляет тендер по ID"""
        try:
            result = await self.collection.update_one(
                {"_id": id},
                {"$set": data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Ошибка при обновлении: {e}")
            return False

    async def delete(self, id: str) -> bool:
        """Удаляет тендер по ID"""
        try:
            result = await self.collection.delete_one({"_id": id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Ошибка при удалении: {e}")
            return False

    async def close(self) -> None:
        """Закрывает соединение с БД"""
        logger.info("Закрытие соединения с коллекцией тендеров")
        pass
