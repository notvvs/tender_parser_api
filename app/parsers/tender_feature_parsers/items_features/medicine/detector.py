import logging
from playwright.async_api import Page

logger = logging.getLogger(__name__)


async def is_medical_tender(page: Page) -> bool:
    """Определяет, является ли тендер медицинским"""
    try:
        med_table = await page.query_selector("[id^='medTable']")
        if med_table:
            logger.debug("Обнаружен медицинский тендер")
            return True

        logger.debug("Обычный тендер (не медицинский)")
        return False
    except Exception as e:
        logger.error(f"Ошибка при определении типа тендера: {e}")
        return False


async def get_medical_table(page: Page):
    """Возвращает таблицу с медицинскими товарами"""
    try:
        med_table_container = await page.query_selector("[id^='medTable']")
        if med_table_container:
            table = await med_table_container.query_selector("table.tableBlock")
            return table
        return None
    except Exception as e:
        logger.error(f"Ошибка при получении медицинской таблицы: {e}")
        return None