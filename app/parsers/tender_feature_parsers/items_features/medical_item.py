import logging
import re
from typing import Optional

from playwright.async_api import Page
from app.schemas.items import Item, ItemCharacteristic, Price

logger = logging.getLogger(__name__)


def parse_quantity(text: str) -> int:
    """Простой парсер количества"""
    # Убираем все пробелы (включая неразрывные) и заменяем запятую на точку
    text = text.replace('\xa0', '').replace(' ', '').replace(',', '.')
    # Оставляем только цифры и точку
    text = re.sub(r'[^\d.]', '', text)
    try:
        return int(float(text))
    except:
        return 0


def parse_price(text: str) -> Price:
    """Простой парсер цены"""
    # Аналогично количеству
    text = text.replace('\xa0', '').replace(' ', '').replace(',', '.')
    text = re.sub(r'[^\d.]', '', text)
    try:
        amount = float(text)
    except:
        amount = 0.0
    return Price(amount=amount, currency="RUB")


async def parse_medical_item_from_row(page: Page, row, item_id: int) -> Optional[Item]:
    """Простой парсер медицинского товара"""
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

        # Парсим форму/дозировку/единицу
        # Формат: "КАПСУЛЫ, 3 мг, шт (капсула)"
        parts = [p.strip() for p in form_dosage_text.split(',')]
        form = parts[0] if parts else ""
        dosage = parts[1] if len(parts) > 1 else ""

        # Единица измерения - берем из скобок или первое слово
        unit = "шт"
        if len(parts) > 2:
            unit_part = parts[2]
            # Если есть скобки, берем содержимое
            match = re.search(r'\(([^)]+)\)', unit_part)
            if match:
                unit = match.group(1)
            else:
                # Иначе первое слово
                unit = unit_part.split()[0] if unit_part else "шт"

        # Название препарата
        name = f"{mnn.strip()} {form} {dosage}".strip()

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
                value=form,
                unit=None,
                type="Качественная",
                required=True,
                changeable=False
            ),
            ItemCharacteristic(
                id=3,
                name="Дозировка",
                value=dosage,
                unit=None,
                type="Качественная",
                required=True,
                changeable=False
            )
        ]

        # Получаем ОКПД2, КТРУ и альтернативные варианты
        okpd2_code = None
        ktru_code = None

        try:
            # Кликаем на стрелку для раскрытия
            arrow = await row.query_selector("svg")
            if arrow:
                # Закрываем модальное окно если есть
                modal = await page.query_selector(".popupModalOverlay")
                if modal:
                    await page.evaluate("document.querySelector('.popupModalOverlay')?.remove()")

                # Получаем ID информационного блока из onclick
                onclick = await arrow.get_attribute("onclick")
                info_id = None
                if onclick:
                    match = re.search(r"'(medInfo\d+_\d+)'", onclick)
                    if match:
                        info_id = match.group(1)

                await arrow.click()
                await page.wait_for_timeout(500)

                # Ищем развернутые строки по ID
                if info_id:
                    info_rows = await page.query_selector_all(f"tr.{info_id}")

                    for info_row in info_rows:
                        # Ищем таблицу вариантов внутри информационной строки
                        variant_table = await info_row.query_selector("table.medicine-delivery-variant")
                        if variant_table:
                            # Получаем все строки
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

                                    # Извлекаем ОКПД2 и КТРУ из основного варианта
                                    if not is_alternative and not okpd2_code:
                                        okpd2_match = re.search(r'(\d{2}\.\d{2}\.\d{2}\.\d{3}):', code_text)
                                        if okpd2_match:
                                            okpd2_code = okpd2_match.group(1)

                                        ktru_match = re.search(r'(\d{2}\.\d{2}\.\d{2}\.\d{3}-\d{8})', code_text)
                                        if ktru_match:
                                            ktru_code = ktru_match.group(1)

                                    # Парсим альтернативный вариант
                                    if is_alternative:
                                        # Вторая ячейка - МНН, форма, дозировка
                                        med_info = await cells_var[1].text_content()
                                        med_lines = [line.strip() for line in med_info.split('\n') if line.strip()]

                                        if len(med_lines) >= 3:
                                            alt_dosage = med_lines[2]  # Например: "1.5 мг"

                                            # Третья ячейка - количество
                                            qty_text = await cells_var[2].text_content()
                                            qty_lines = [line.strip() for line in qty_text.split('\n') if line.strip()]

                                            if qty_lines:
                                                alt_quantity = qty_lines[0]  # Например: "1 120,00"

                                                # Собираем все альтернативные варианты
                                                alt_variants = []
                                                for char in characteristics:
                                                    if char.name == "Альтернативные варианты поставки":
                                                        alt_variants.append(char.value)
                                                        characteristics.remove(char)
                                                        break

                                                # Добавляем новый вариант
                                                alt_variants.append(f"{form} {alt_dosage} - {alt_quantity} {unit}")

                                                # Создаем обновленную характеристику со всеми вариантами
                                                characteristics.append(
                                                    ItemCharacteristic(
                                                        id=len(characteristics) + 1,
                                                        name="Альтернативные варианты поставки",
                                                        value="; ".join(alt_variants),
                                                        unit=None,
                                                        type="Качественная",
                                                        required=False,
                                                        changeable=True,
                                                        fillInstruction=None
                                                    )
                                                )

                        # Проверяем ЖНВЛП в этой же строке
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
                                            characteristics.append(
                                                ItemCharacteristic(
                                                    id=len(characteristics) + 1,
                                                    name="Включено в перечень ЖНВЛП",
                                                    value="Да",
                                                    unit=None,
                                                    type="Качественная",
                                                    required=True,
                                                    changeable=False
                                                )
                                            )
                                            break

        except Exception as e:
            logger.debug(f"Ошибка при получении дополнительной информации: {e}")

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
            additionalRequirements=None
        )

    except Exception as e:
        logger.error(f"Ошибка при парсинге медицинского товара: {e}")
        return None