import asyncio
import logging
import re
from typing import Optional

from playwright.async_api import Page

from app.parsers.tender_feature_parsers.items_features.characteristics import parse_characteristics_from_table
from app.parsers.tender_feature_parsers.items_features.codes import extract_ktru_code, extract_okpd2_code
from app.parsers.tender_feature_parsers.items_features.price import parse_price
from app.parsers.tender_feature_parsers.items_features.quantity import parse_quantity
from app.schemas.items import Item

logger = logging.getLogger(__name__)

async def parse_item_from_row(page: Page, row, item_id: int) -> Optional[Item]:
    """Парсит товар из строки таблицы"""
    try:
        cells = await row.query_selector_all("td.tableBlock__col")
        if len(cells) < 7:
            return None

        # Извлекаем тексты из ячеек
        cell_texts = []
        for cell in cells:
            text = await cell.text_content()
            cell_texts.append(text)

        # Извлекаем коды
        code_cell = cell_texts[1]
        okpd2_code = extract_okpd2_code(code_cell)
        ktru_code = extract_ktru_code(code_cell)

        # Название товара
        name_lines = cell_texts[2].strip().split('\n')
        name = name_lines[0].strip()

        # Единица измерения
        unit = cell_texts[3].strip()

        # Количество
        quantity = parse_quantity(cell_texts[4])

        # Цены
        unit_price = parse_price(cell_texts[5])
        total_price = parse_price(cell_texts[6])

        # Характеристики
        characteristics = []
        additional_requirements = None

        # Пытаемся получить характеристики
        try:
            chevron = await cells[0].query_selector(".chevronRight")
            if chevron:
                onclick_attr = await chevron.get_attribute("onclick")
                if onclick_attr:
                    match = re.search(r"'truInfo_(\d+)'", onclick_attr)
                    if match:
                        info_id = match.group(1)

                        # Кликаем для разворачивания
                        await chevron.click()
                        await asyncio.sleep(1)

                        # Находим таблицу с характеристиками
                        info_rows = await page.query_selector_all(f"tr.truInfo_{info_id}")

                        for info_row in info_rows:
                            tables = await info_row.query_selector_all("table.tableBlock")
                            for table in tables:
                                try:
                                    header = await table.query_selector("td:has-text('Наименование характеристики')")
                                    if header:
                                        characteristics = await parse_characteristics_from_table(table)
                                        break
                                except:
                                    continue
        except Exception as e:
            logger.error(f'Ошибка при получении характеристик: {e}')

        return Item(
            id=item_id,
            name=name,
            okpd2Code=okpd2_code,
            ktruCode=ktru_code,
            quantity=quantity,
            unitOfMeasurement=unit,
            unitPrice=unit_price,
            totalPrice=total_price,
            characteristics=characteristics,
            additionalRequirements=additional_requirements
        )

    except Exception as e:
        logger.error(f"Ошибка при парсинге товара: {e}")
        return None