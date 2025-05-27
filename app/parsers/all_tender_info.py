import logging

from app.parsers.tender_feature_parsers.documents_info import get_tender_documents
from app.parsers.tender_feature_parsers.tender_info import get_tender_info
from app.parsers.tender_feature_parsers.items_info import get_tender_items
from app.schemas.tender import TenderData
from app.utils.create_driver import get_driver

logger = logging.getLogger(__name__)

def get_tender(url: str) -> TenderData:
    """Функция для получения всей информации о тендере"""
    logger.info(f"Начало парсинга тендера: {url}")

    try:
        with get_driver() as driver:
            driver.get(url)

            logger.debug("Парсинг основной информации о тендере")
            tenderInfo = get_tender_info(driver)

            logger.debug("Парсинг позиций закупки")
            items = get_tender_items(driver)

            generalRequirements = None

        # Документы парсим отдельно, так как это другая страница
        logger.debug("Парсинг документов")
        attachments = get_tender_documents(url)

        logger.info(f"Парсинг завершен успешно. Найдено позиций: {len(items)}, документов: {len(attachments)}")

        return TenderData(
            tenderInfo=tenderInfo,
            items=items,
            generalRequirements=generalRequirements,
            attachments=attachments
        )

    except Exception as e:
        logger.error(f"Ошибка при парсинге тендера: {e}", exc_info=True)
        raise
