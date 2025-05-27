from motor.motor_asyncio import AsyncIOMotorClient

from app.repository.repository import TenderRepository

client = AsyncIOMotorClient("mongodb://localhost:27017")
database = client["tenders_db"]

repository = TenderRepository(database, collection_name="tenders")