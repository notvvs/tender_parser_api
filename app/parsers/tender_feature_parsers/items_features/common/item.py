import asyncio
import logging
import re
from typing import Optional

from playwright.async_api import Page

from app.parsers.tender_feature_parsers.items_features.common.characteristics import (
    parse_characteristics_from_table,
)
from app.parsers.tender_feature_parsers.items_features.common.codes import (
    extract_ktru_code,
    extract_okpd2_code,
)
from app.parsers.tender_feature_parsers.items_features.common.price import parse_price
from app.parsers.tender_feature_parsers.items_features.common.quantity import parse_quantity
from app.schemas.items import Item, ItemCharacteristic
from app.utils.validator import clean_text

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
        name_lines = cell_texts[2].strip().split("\n")
        name = name_lines[0].strip()

        # Определяем, есть ли товарный знак (если 8 ячеек вместо 7)
        has_trademark = len(cells) == 8
        trademark = None

        if has_trademark:
            # Есть товарный знак
            trademark = cell_texts[3].strip()
            unit = cell_texts[4].strip()
            quantity = parse_quantity(cell_texts[5])
            unit_price = parse_price(cell_texts[6])
            total_price = parse_price(cell_texts[7])
        else:
            # Нет товарного знака
            trademark = None
            unit = cell_texts[3].strip()
            quantity = parse_quantity(cell_texts[4])
            unit_price = parse_price(cell_texts[5])
            total_price = parse_price(cell_texts[6])

        # Характеристики
        characteristics = []
        additional_requirements = None

        # Добавляем товарный знак как первую характеристику, если он есть
        if trademark and trademark != "-" and trademark.strip():
            # Проверяем наличие информации об эквиваленте
            trademark_value = trademark.strip()

            if "Допускается поставка эквивалента" in trademark_value:
                # Убираем информацию об эквиваленте из значения
                trademark_value = trademark_value.replace("Допускается поставка эквивалента", "").strip()
                fill_instruction = "Допускается поставка эквивалента"
                changeable = True
            else:
                fill_instruction = "Значение характеристики не может изменяться участником закупки"
                changeable = False

            characteristics.append(
                ItemCharacteristic(
                    id=1,
                    name="Товарный знак",
                    value=clean_text(trademark_value),
                    unit=None,
                    type="Качественная",
                    required=True,
                    changeable=changeable,
                    fillInstruction=fill_instruction
                )
            )

        # Пытаемся получить характеристики из развернутой таблицы
        try:
            chevron = await cells[0].query_selector(".chevronRight")
            if chevron:
                onclick_attr = await chevron.get_attribute("onclick")
                if onclick_attr:
                    match = re.search(r"'truInfo_(\d+)'", onclick_attr)
                    if match:
                        info_id = match.group(1)

                        try:
                            # Кликаем для разворачивания
                            await chevron.click()
                            await asyncio.sleep(1)
                        except Exception as e:
                            logger.debug(f"Не удалось кликнуть на chevron: {e}")
                            # Альтернативный способ через JavaScript
                            try:
                                await page.evaluate(onclick_attr)
                                await asyncio.sleep(1)
                            except:
                                logger.debug("Не удалось раскрыть характеристики через JS")

                        # Находим таблицу с характеристиками
                        info_rows = await page.query_selector_all(
                            f"tr.truInfo_{info_id}"
                        )

                        for info_row in info_rows:
                            tables = await info_row.query_selector_all(
                                "table.tableBlock"
                            )
                            for table in tables:
                                try:
                                    header = await table.query_selector(
                                        "td:has-text('Наименование характеристики')"
                                    )
                                    if header:
                                        table_characteristics = (
                                            await parse_characteristics_from_table(
                                                table
                                            )
                                        )
                                        # Добавляем характеристики из таблицы, корректируя их id
                                        for char in table_characteristics:
                                            char.id = len(characteristics) + 1
                                            characteristics.append(char)
                                        break
                                except:
                                    continue
        except Exception as e:
            logger.error(f"Ошибка при получении характеристик: {e}")

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
            additionalRequirements=additional_requirements,
        )

    except Exception as e:
        logger.error(f"Ошибка при парсинге товара: {e}")
        return None