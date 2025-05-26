import logging
import re
from typing import Optional

from selenium.webdriver.common.by import By

from app.parsers.tender_feature_parsers.items_features.characteristics import parse_characteristics_from_table
from app.parsers.tender_feature_parsers.items_features.codes import extract_okpd2_code, extract_ktru_code
from app.parsers.tender_feature_parsers.items_features.price import parse_price
from app.parsers.tender_feature_parsers.items_features.quantity import parse_quantity
from app.schemas.items import Item


logger = logging.getLogger(__name__)


def parse_item_from_row(driver, row, item_id: int) -> Optional[Item]:
    """Парсит товар из строки таблицы"""
    try:
        cells = row.find_elements(By.CSS_SELECTOR, "td.tableBlock__col")
        if len(cells) < 7:  # Минимум колонок для валидной строки
            return None

        # Извлекаем коды
        code_cell = cells[1].text
        okpd2_code = extract_okpd2_code(code_cell)
        ktru_code = extract_ktru_code(code_cell)

        # Название товара
        name_cell = cells[2]
        name_lines = name_cell.text.strip().split('\n')
        name = name_lines[0].strip()  # Берем первую строку

        # Единица измерения
        unit = cells[3].text.strip()

        # Количество
        quantity = parse_quantity(cells[4].text)

        # Цена за единицу
        unit_price = parse_price(cells[5].text)

        # Общая стоимость
        total_price = parse_price(cells[6].text)

        # Инициализируем пустые характеристики
        characteristics = []
        additional_requirements = None

        # Пытаемся найти и развернуть информацию о товаре
        try:
            # Находим кнопку разворачивания в первой ячейке
            chevron = cells[0].find_element(By.CSS_SELECTOR, ".chevronRight")
            if chevron:
                # Получаем ID информационного блока из onclick атрибута
                onclick_attr = chevron.get_attribute("onclick")
                if onclick_attr:
                    match = re.search(r"'truInfo_(\d+)'", onclick_attr)
                    if match:
                        info_id = match.group(1)

                        # Кликаем для разворачивания
                        driver.execute_script("arguments[0].click();", chevron)
                        driver.implicitly_wait(1)

                        # Находим блок с характеристиками
                        try:
                            info_rows = driver.find_elements(
                                By.CSS_SELECTOR,
                                f".truInfo_{info_id}"
                            )

                            for info_row in info_rows:
                                # Парсим характеристики из таблицы внутри блока
                                char_table = info_row.find_element(By.CSS_SELECTOR, "table.tableBlock")
                                characteristics = parse_characteristics_from_table(char_table)

                                # Ищем дополнительные требования
                                try:
                                    req_spans = info_row.find_elements(
                                        By.XPATH,
                                        ".//span[contains(text(), 'Обоснование включения')]/following-sibling::span"
                                    )
                                    if req_spans:
                                        additional_requirements = req_spans[0].text.strip()
                                except:
                                    pass
                        except:
                            pass
        except:
            pass

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
