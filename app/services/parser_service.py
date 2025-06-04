import logging

from app.parsers.all_tender_info import get_tender
from app.schemas.tender import TenderData

logger = logging.getLogger(__name__)

class ParserService:

    async def start_parsing(self, url: str) -> TenderData:
        logger.info(f"Начало парсинга тендера: {url}")

        result = await get_tender(url)

        return result

parser = ParserService()