import logging
from typing import List

from playwright.async_api import Page

from app.parsers.tender_feature_parsers.items_features.item import parse_item_from_row
from app.schemas.items import Item
from app.utils.pagination_button import go_to_next_page

logger = logging.getLogger(__name__)

async def get_tender_items(page: Page) -> List[Item]:
    """Основная функция для парсинга товаров тендера"""
    items = []

    try:
        await page.wait_for_selector("#positionKTRU", timeout=10000)

        item_id = 1
        page_num = 1

        while True:
            logger.info(f"Парсинг страницы {page_num}...")

            table = await page.query_selector("#positionKTRU table.tableBlock")
            item_rows = await table.query_selector_all("tbody.tableBlock__body > tr.tableBlock__row")

            for row in item_rows:
                class_name = await row.get_attribute("class")
                if "truInfo_" in class_name:
                    continue

                item = await parse_item_from_row(page, row, item_id)
                if item:
                    items.append(item)
                    item_id += 1

            if not await go_to_next_page(page):
                break

            page_num += 1

        logger.info(f"Всего найдено товаров: {len(items)}")

    except Exception as e:
        logger.error(f"Критическая ошибка при парсинге: {e}")

    return items