import logging

from app.parsers.tender_feature_parsers.documents_info import get_tender_documents
from app.parsers.tender_feature_parsers.general_requirements import (
    get_general_requirements,
)
from app.parsers.tender_feature_parsers.tender_info import get_tender_info
from app.parsers.tender_feature_parsers.items_info import get_tender_items
from app.schemas.tender import TenderData
from app.utils.create_driver import get_page

logger = logging.getLogger(__name__)


async def get_tender(url: str) -> TenderData:
    """Функция для получения всей информации о тендере"""

    try:
        async with get_page() as page:
            await page.goto(url)

            logger.debug("Парсинг основной информации")
            tenderInfo = await get_tender_info(page)

            logger.debug("Парсинг позиций закупки")
            items = await get_tender_items(page)

            generalRequirements = await get_general_requirements(page)

        # Документы парсим отдельно
        logger.debug("Парсинг документов")
        attachments = await get_tender_documents(url)

        logger.info(
            f"Парсинг завершен. Позиций: {len(items)}, документов: {len(attachments)}"
        )

        return TenderData(
            tenderInfo=tenderInfo,
            items=items,
            generalRequirements=generalRequirements,
            attachments=attachments,
        )

    except Exception as e:
        logger.error(f"Ошибка при парсинге тендера: {e}", exc_info=True)
        raise
