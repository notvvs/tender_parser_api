import logging
from typing import List

from playwright.async_api import Page

from app.parsers.tender_feature_parsers.items_features.common.item import parse_item_from_row
from app.parsers.tender_feature_parsers.items_features.medicine.medical_item import parse_medical_item_from_row
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

                    # Заново находим таблицу после каждого перехода страницы
                    current_table = await page.query_selector("#positionKTRU table.tableBlock")
                    if not current_table:
                        logger.error("Таблица не найдена после перехода на страницу")
                        break

                    # Находим строки товаров на текущей странице
                    item_rows = await current_table.query_selector_all(
                        "tbody.tableBlock__body > tr.tableBlock__row"
                    )

                    logger.info(f"Найдено {len(item_rows)} строк на странице {page_num}")

                    # Парсим товары с текущей страницы
                    parsed_on_page = 0
                    for row in item_rows:
                        # Пропускаем информационные строки
                        class_name = await row.get_attribute("class")
                        if class_name and "truInfo_" in class_name:
                            continue

                        item = await parse_item_from_row(page, row, item_id)
                        if item:
                            items.append(item)
                            item_id += 1
                            parsed_on_page += 1

                    logger.info(f"Распарсено {parsed_on_page} товаров на странице {page_num}")

                    # Пагинация
                    if not await go_to_next_page(page):
                        logger.info("Достигнута последняя страница")
                        break

                    # Ждем загрузки новой страницы
                    await page.wait_for_timeout(2000)  # Увеличиваем время ожидания

                    # Ждем, пока таблица обновится
                    try:
                        await page.wait_for_selector("#positionKTRU table.tableBlock", timeout=5000)
                    except:
                        logger.error("Таблица не загрузилась после перехода на новую страницу")
                        break

                    page_num += 1

            except Exception as e:
                logger.error(f"Ошибка при парсинге обычных товаров: {e}")

    logger.info(f"Всего найдено товаров: {len(items)}")
    return items