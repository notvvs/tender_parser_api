from typing import List
import logging


from app.schemas.items import ItemCharacteristic

logger = logging.getLogger(__name__)


def parse_characteristic_type(instruction_text: str) -> str:
    """Определяет тип характеристики по инструкции"""
    if "конкретное значение" in instruction_text.lower():
        return "Количественная"
    return "Качественная"


def parse_characteristic_changeable(instruction_text: str) -> bool:
    """Определяет, может ли характеристика изменяться участником"""
    if "не может изменяться" in instruction_text.lower():
        return False
    elif "указывает в заявке" in instruction_text.lower():
        return True
    return False


async def parse_characteristics_from_table(table_element) -> List[ItemCharacteristic]:
    """Парсит характеристики из таблицы"""
    characteristics = []

    try:
        rows = await table_element.query_selector_all("tbody tr.tableBlock__row")

        char_id = 1
        current_name = None
        current_unit = None
        current_instruction = None
        current_values = []

        i = 0
        while i < len(rows):
            row = rows[i]
            cells = await row.query_selector_all("td")

            if len(cells) < 2:
                i += 1
                continue

            first_cell_text = await cells[0].text_content()
            first_cell_text = first_cell_text.strip().upper()
            if "НАИМЕНОВАНИЕ" in first_cell_text and "ХАРАКТЕРИСТИК" in first_cell_text:
                i += 1
                continue

            # Проверяем rowspan
            first_cell = cells[0]
            rowspan = await first_cell.get_attribute("rowspan")

            if rowspan and int(rowspan) >= 1:
                # Сохраняем предыдущую характеристику
                if current_name and current_values:
                    combined_value = ", ".join(current_values)
                    char_type = parse_characteristic_type(current_instruction or "")
                    changeable = parse_characteristic_changeable(
                        current_instruction or ""
                    )

                    characteristic = ItemCharacteristic(
                        id=char_id,
                        name=current_name,
                        value=combined_value,
                        unit=current_unit,
                        type=char_type,
                        required=True,
                        changeable=changeable,
                        fillInstruction=current_instruction,
                    )
                    characteristics.append(characteristic)
                    char_id += 1

                # Начинаем новую характеристику
                current_name = await first_cell.text_content()
                current_name = current_name.strip()
                value_text = await cells[1].text_content()
                current_values = [value_text.strip()]

                # Сохраняем единицу и инструкцию
                if len(cells) > 2:
                    unit_cell = cells[2]
                    unit_rowspan = await unit_cell.get_attribute("rowspan")
                    if unit_rowspan:
                        unit_text = await unit_cell.text_content()
                        current_unit = unit_text.strip() if unit_text.strip() else None

                    if len(cells) > 3:
                        instruction_cell = cells[3]
                        instruction_rowspan = await instruction_cell.get_attribute(
                            "rowspan"
                        )
                        if instruction_rowspan:
                            current_instruction = await instruction_cell.text_content()
                            current_instruction = current_instruction.strip()

                # Собираем значения из следующих строк
                rowspan_count = int(rowspan)
                if rowspan_count > 1:
                    for j in range(1, rowspan_count):
                        if i + j < len(rows):
                            next_row = rows[i + j]
                            next_cells = await next_row.query_selector_all("td")
                            if next_cells:
                                value_text = await next_cells[0].text_content()
                                if value_text.strip():
                                    current_values.append(value_text.strip())

                    i += rowspan_count
                else:
                    i += 1
            else:
                # Обычная строка без rowspan
                if len(cells) >= 4:
                    name = await cells[0].text_content()
                    value = await cells[1].text_content()
                    unit_text = await cells[2].text_content()
                    unit = unit_text.strip() if unit_text.strip() else None
                    instruction = ""
                    if len(cells) > 3:
                        instruction = await cells[3].text_content()

                    name = name.strip()
                    if name.upper() == "НАИМЕНОВАНИЕ ХАРАКТЕРИСТИКИ":
                        i += 1
                        continue

                    char_type = parse_characteristic_type(instruction)
                    changeable = parse_characteristic_changeable(instruction)

                    characteristic = ItemCharacteristic(
                        id=char_id,
                        name=name,
                        value=value.strip(),
                        unit=unit,
                        type=char_type,
                        required=True,
                        changeable=changeable,
                        fillInstruction=instruction if instruction else None,
                    )
                    characteristics.append(characteristic)
                    char_id += 1

                i += 1

        # Сохраняем последнюю характеристику
        if current_name and current_values:
            combined_value = ", ".join(current_values)
            char_type = parse_characteristic_type(current_instruction or "")
            changeable = parse_characteristic_changeable(current_instruction or "")

            characteristic = ItemCharacteristic(
                id=char_id,
                name=current_name,
                value=combined_value,
                unit=current_unit,
                type=char_type,
                required=True,
                changeable=changeable,
                fillInstruction=current_instruction,
            )
            characteristics.append(characteristic)

    except Exception as e:
        logger.error(f"Ошибка при парсинге характеристик из таблицы: {e}")

    return characteristics
