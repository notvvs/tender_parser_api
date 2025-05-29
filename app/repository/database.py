from motor.motor_asyncio import AsyncIOMotorClient
from app.core.settings import settings
from app.repository.repository import TenderRepository
from app.repository.task_repository import TaskRepository

client = AsyncIOMotorClient(settings.mongodb_url)
database = client[settings.mongodb_db_name]

repository = TenderRepository(database, collection_name="tenders")
task_repository = TaskRepository(database, collection_name="tasks")