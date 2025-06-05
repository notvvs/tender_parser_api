import logging
from typing import Optional

from playwright.async_api import Page

from app.parsers.tender_feature_parsers.items_features.medicine.parsers import parse_codes_and_alternatives
from app.parsers.tender_feature_parsers.items_features.medicine.utils import parse_medical_info, parse_quantity, \
    parse_price
from app.schemas.items import Item, ItemCharacteristic


logger = logging.getLogger(__name__)


async def parse_medical_item_from_row(page: Page, row, item_id: int) -> Optional[Item]:
    """Основной парсер медицинского товара"""
    try:
        cells = await row.query_selector_all("td.tableBlock__col")
        if len(cells) < 6:
            return None

        # Извлекаем тексты из ячеек
        mnn = await cells[1].text_content()
        form_dosage_text = await cells[2].text_content()
        quantity_text = await cells[3].text_content()
        unit_price_text = await cells[4].text_content()
        total_price_text = await cells[5].text_content()

        # Парсим основную информацию
        med_info = parse_medical_info(form_dosage_text)
        name = f"{mnn.strip()} {med_info['form']} {med_info['dosage']}".strip()

        # Парсим числовые значения
        quantity = parse_quantity(quantity_text)
        unit_price = parse_price(unit_price_text)
        total_price = parse_price(total_price_text)

        # Базовые характеристики
        characteristics = [
            ItemCharacteristic(
                id=1,
                name="МНН (Международное непатентованное наименование)",
                value=mnn.strip(),
                unit=None,
                type="Качественная",
                required=True,
                changeable=False
            ),
            ItemCharacteristic(
                id=2,
                name="Лекарственная форма",
                value=med_info['form'],
                unit=None,
                type="Качественная",
                required=True,
                changeable=False
            ),
            ItemCharacteristic(
                id=3,
                name="Дозировка",
                value=med_info['dosage'],
                unit=None,
                type="Качественная",
                required=True,
                changeable=False
            )
        ]

        # Получаем дополнительную информацию (коды, альтернативы, ЖНВЛП, единицу измерения)
        codes_data = await parse_codes_and_alternatives(
            page, row, characteristics, "шт", med_info['form']  # Передаем "шт" как значение по умолчанию
        )

        return Item(
            id=item_id,
            name=name,
            okpd2Code=codes_data.get('okpd2_code'),
            ktruCode=codes_data.get('ktru_code'),
            quantity=quantity,
            unitOfMeasurement=codes_data.get('unit', 'шт'),  # Берем единицу из таблицы вариантов
            unitPrice=unit_price,
            totalPrice=total_price,
            characteristics=codes_data.get('characteristics', characteristics),
            additionalRequirements=None
        )

    except Exception as e:
        logger.error(f"Ошибка при парсинге медицинского товара: {e}")
        return None