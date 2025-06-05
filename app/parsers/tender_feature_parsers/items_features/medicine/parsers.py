import logging
import re
from typing import Dict, List, Optional

from playwright.async_api import Page

from app.schemas.items import ItemCharacteristic

logger = logging.getLogger(__name__)


async def parse_codes_and_alternatives(
        page: Page,
        row,
        characteristics: List[ItemCharacteristic],
        unit: str,
        form: str = None
) -> Dict:
    """Парсит коды ОКПД2, КТРУ и альтернативные варианты"""
    okpd2_code = None
    ktru_code = None
    updated_characteristics = characteristics.copy()

    try:
        # Кликаем на стрелку для раскрытия
        arrow = await row.query_selector("svg")
        if not arrow:
            return {
                'okpd2_code': okpd2_code,
                'ktru_code': ktru_code,
                'characteristics': updated_characteristics
            }

        # Закрываем модальное окно если есть
        modal = await page.query_selector(".popupModalOverlay")
        if modal:
            await page.evaluate("document.querySelector('.popupModalOverlay')?.remove()")

        # Получаем ID информационного блока
        onclick = await arrow.get_attribute("onclick")
        info_id = None
        if onclick:
            match = re.search(r"'(medInfo\d+_\d+)'", onclick)
            if match:
                info_id = match.group(1)

        await arrow.click()
        await page.wait_for_timeout(500)

        if not info_id:
            return {
                'okpd2_code': okpd2_code,
                'ktru_code': ktru_code,
                'characteristics': updated_characteristics
            }

        # Ищем развернутые строки
        info_rows = await page.query_selector_all(f"tr.{info_id}")

        for info_row in info_rows:
            # Парсим таблицу вариантов
            variant_table = await info_row.query_selector("table.medicine-delivery-variant")
            if variant_table:
                codes_result = await parse_variant_table(variant_table, unit, updated_characteristics, form)
                okpd2_code = codes_result['okpd2_code'] or okpd2_code
                ktru_code = codes_result['ktru_code'] or ktru_code
                updated_characteristics = codes_result['characteristics']

            # Проверяем ЖНВЛП
            jnvlp_char = await check_jnvlp(info_row)
            if jnvlp_char:
                jnvlp_char.id = len(updated_characteristics) + 1
                updated_characteristics.append(jnvlp_char)

    except Exception as e:
        logger.debug(f"Ошибка при получении дополнительной информации: {e}")

    return {
        'okpd2_code': okpd2_code,
        'ktru_code': ktru_code,
        'characteristics': updated_characteristics
    }


async def parse_variant_table(variant_table, unit: str, characteristics: List[ItemCharacteristic],
                              form: str = None) -> Dict:
    """Парсит таблицу с вариантами поставки"""
    okpd2_code = None
    ktru_code = None
    alternatives = []
    updated_characteristics = characteristics.copy()

    try:
        rows = await variant_table.query_selector_all("tbody tr")
        is_alternative = False

        for row_var in rows:
            row_text = await row_var.text_content()

            # Проверяем заголовки
            if "Основной вариант поставки" in row_text:
                is_alternative = False
                continue
            elif "Альтернативный вариант" in row_text:
                is_alternative = True
                continue

            # Получаем ячейки данных
            cells_var = await row_var.query_selector_all("td.tableBlock__col")
            if len(cells_var) >= 3:
                # Первая ячейка - коды
                code_text = await cells_var[0].text_content()

                # Извлекаем коды из основного варианта
                if not is_alternative and not okpd2_code:
                    okpd2_match = re.search(r'(\d{2}\.\d{2}\.\d{2}\.\d{3}):', code_text)
                    if okpd2_match:
                        okpd2_code = okpd2_match.group(1)

                    ktru_match = re.search(r'(\d{2}\.\d{2}\.\d{2}\.\d{3}-\d{8})', code_text)
                    if ktru_match:
                        ktru_code = ktru_match.group(1)

                # Парсим альтернативный вариант
                if is_alternative:
                    alt_info = await parse_alternative_variant(cells_var, unit, form)
                    if alt_info:
                        alternatives.append(alt_info)

        # Добавляем альтернативы в характеристики
        if alternatives:
            updated_characteristics = add_alternatives_to_characteristics(
                updated_characteristics,
                alternatives
            )

    except Exception as e:
        logger.error(f"Ошибка при парсинге таблицы вариантов: {e}")

    return {
        'okpd2_code': okpd2_code,
        'ktru_code': ktru_code,
        'characteristics': updated_characteristics
    }


async def parse_alternative_variant(cells, unit: str, form: str = None) -> Optional[str]:
    """Парсит информацию об альтернативном варианте"""
    try:
        # Вторая ячейка - МНН, форма, дозировка
        med_info = await cells[1].text_content()
        med_lines = [line.strip() for line in med_info.split('\n') if line.strip()]

        if len(med_lines) >= 3:
            alt_form = med_lines[1] if not form else form  # Используем переданную форму если есть
            alt_dosage = med_lines[2]  # Например: "1.5 мг"

            # Третья ячейка - количество
            qty_text = await cells[2].text_content()
            qty_lines = [line.strip() for line in qty_text.split('\n') if line.strip()]

            if qty_lines:
                alt_quantity = qty_lines[0]  # Например: "1 120,00"
                return f"{alt_form} {alt_dosage} - {alt_quantity} {unit}"

    except Exception as e:
        logger.debug(f"Ошибка при парсинге альтернативного варианта: {e}")

    return None


async def check_jnvlp(info_row) -> Optional[ItemCharacteristic]:
    """Проверяет включение в перечень ЖНВЛП"""
    try:
        sections = await info_row.query_selector_all("section.blockInfo__section")
        for section in sections:
            title_elem = await section.query_selector("span.section__title")
            if title_elem:
                title_text = await title_elem.text_content()
                if "жизненно необходимых" in title_text:
                    info_elem = await section.query_selector("span.section__info")
                    if info_elem:
                        info_text = await info_elem.text_content()
                        if "Да" in info_text:
                            return ItemCharacteristic(
                                id=999,  # ID будет переназначен позже
                                name="Включено в перечень ЖНВЛП",
                                value="Да",
                                unit=None,
                                type="Качественная",
                                required=True,
                                changeable=False
                            )
    except Exception as e:
        logger.debug(f"Ошибка при проверке ЖНВЛП: {e}")

    return None


def add_alternatives_to_characteristics(
        characteristics: List[ItemCharacteristic],
        alternatives: List[str]
) -> List[ItemCharacteristic]:
    """Добавляет альтернативные варианты в характеристики"""
    # Создаем копию списка
    updated_characteristics = []

    # Копируем все характеристики кроме альтернатив
    for char in characteristics:
        if char.name != "Альтернативные варианты поставки":
            updated_characteristics.append(char)

    # Добавляем новую характеристику со всеми альтернативами
    if alternatives:
        updated_characteristics.append(
            ItemCharacteristic(
                id=len(updated_characteristics) + 1,
                name="Альтернативные варианты поставки",
                value="; ".join(alternatives),
                unit=None,
                type="Качественная",
                required=False,
                changeable=True,
                fillInstruction=None
            )
        )

    return updated_characteristics