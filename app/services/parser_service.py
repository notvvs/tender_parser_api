import logging
from app.parsers.all_tender_info import get_tender
from app.schemas.tender import TenderData
from app.utils.validator import validate_tender_url

logger = logging.getLogger(__name__)


class ParserService:
    def __init__(self):
        self._parse_count = 0

    async def start_parsing(self, url: str) -> TenderData:
        """Парсинг с валидацией и обработкой ошибок"""
        # Валидация URL
        is_valid, error = validate_tender_url(url)
        if not is_valid:
            logger.error(f"Невалидный URL: {error}")
            raise ValueError(error)

        logger.info(f"Начало парсинга тендера #{self._parse_count + 1}: {url}")

        try:
            result = await get_tender(url)
            self._parse_count += 1
            logger.info(f"Успешно распарсен тендер. Позиций: {len(result.items)}")
            return result
        except Exception as e:
            logger.error(f"Ошибка парсинга: {str(e)}", exc_info=True)
            raise


parser = ParserService()