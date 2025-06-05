import logging
from typing import List

from playwright.async_api import Page

from app.parsers.tender_feature_parsers.items_features.common.item import parse_item_from_row
from app.parsers.tender_feature_parsers.items_features.medical_item import parse_medical_item_from_row
from app.schemas.items import Item
from app.utils.pagination_button import go_to_next_page

logger = logging.getLogger(__name__)


async def get_tender_items(page: Page) -> List[Item]:
    """Основная функция для парсинга товаров тендера"""
    items = []

    # Проверяем наличие медицинской таблицы ВНУТРИ любого контейнера
    med_table = await page.query_selector("[id^='medTable']")

    if med_table:
        # Медицинские товары
        logger.info("Парсинг медицинских товаров")

        try:
            # Находим таблицу внутри медицинского блока
            table = await med_table.query_selector("table.tableBlock")
            if table:
                # Находим все строки с товарами (те, что со стрелкой)
                item_rows = await table.query_selector_all(
                    "tbody.tableBlock__body > tr.tableBlock__row:has(svg)"
                )

                logger.info(f"Найдено строк с товарами: {len(item_rows)}")

                item_id = 1
                for row in item_rows:
                    item = await parse_medical_item_from_row(page, row, item_id)
                    if item:
                        items.append(item)
                        item_id += 1

        except Exception as e:
            logger.error(f"Ошибка при парсинге медицинских товаров: {e}")

    else:
        # Обычные товары - проверяем есть ли вообще таблица
        regular_table = await page.query_selector("#positionKTRU table.tableBlock")

        if regular_table:
            logger.info("Парсинг обычных товаров")

            try:
                item_id = 1
                page_num = 1

                while True:
                    logger.info(f"Парсинг страницы {page_num}...")

                    item_rows = await regular_table.query_selector_all(
                        "tbody.tableBlock__body > tr.tableBlock__row"
                    )

                    for row in item_rows:
                        # Пропускаем информационные строки
                        class_name = await row.get_attribute("class")
                        if "truInfo_" in class_name:
                            continue

                        item = await parse_item_from_row(page, row, item_id)
                        if item:
                            items.append(item)
                            item_id += 1

                    # Пагинация
                    if not await go_to_next_page(page):
                        break

                    page_num += 1

            except Exception as e:
                logger.error(f"Ошибка при парсинге обычных товаров: {e}")

    logger.info(f"Всего найдено товаров: {len(items)}")
    return items