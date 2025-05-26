from typing import List

from selenium.webdriver.common.by import By

from app.schemas.items import ItemCharacteristic


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

def parse_characteristics_from_table(table_element) -> List[ItemCharacteristic]:
    """Парсит характеристики товара из таблицы"""
    characteristics = []

    try:
        rows = table_element.find_elements(By.CSS_SELECTOR, "tbody tr.tableBlock__row")

        char_id = 1
        current_name = None
        current_unit = None
        current_instruction = None
        current_values = []

        i = 0
        while i < len(rows):
            row = rows[i]
            cells = row.find_elements(By.TAG_NAME, "td")

            if len(cells) < 2:
                i += 1
                continue

            first_cell_text = cells[0].text.strip().upper()
            if "НАИМЕНОВАНИЕ" in first_cell_text and "ХАРАКТЕРИСТИК" in first_cell_text:
                i += 1
                continue

            # Проверяем, начинается ли новая характеристика
            first_cell = cells[0]
            rowspan = first_cell.get_attribute("rowspan")

            if rowspan and int(rowspan) >= 1:
                # Сохраняем предыдущую характеристику если она была
                if current_name and current_values:
                    # Объединяем значения через запятую или создаем отдельные характеристики
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
                        fillInstruction=current_instruction
                    )
                    characteristics.append(characteristic)
                    char_id += 1

                # Начинаем новую характеристику
                current_name = first_cell.text.strip()
                current_values = [cells[1].text.strip()]

                # Сохраняем единицу измерения и инструкцию
                if len(cells) > 2:
                    unit_cell_index = 2
                    # Проверяем rowspan для единицы измерения
                    if cells[unit_cell_index].get_attribute("rowspan"):
                        current_unit = cells[unit_cell_index].text.strip() if cells[
                            unit_cell_index].text.strip() else None

                    if len(cells) > 3:
                        instruction_cell_index = 3
                        # Проверяем rowspan для инструкции
                        if cells[instruction_cell_index].get_attribute("rowspan"):
                            current_instruction = cells[instruction_cell_index].text.strip()

                # Если rowspan > 1, нужно обработать следующие строки
                rowspan_count = int(rowspan)
                if rowspan_count > 1:
                    # Собираем значения из следующих строк
                    for j in range(1, rowspan_count):
                        if i + j < len(rows):
                            next_row = rows[i + j]
                            next_cells = next_row.find_elements(By.TAG_NAME, "td")
                            if next_cells:
                                # В продолжающихся строках значение в первой ячейке
                                value_text = next_cells[0].text.strip()
                                if value_text:
                                    current_values.append(value_text)

                    # Пропускаем обработанные строки
                    i += rowspan_count
                else:
                    i += 1
            else:
                # Это обычная строка без rowspan
                if len(cells) >= 4:
                    name = cells[0].text.strip()
                    value = cells[1].text.strip()
                    unit = cells[2].text.strip() if cells[2].text.strip() else None
                    instruction = cells[3].text.strip() if len(cells) > 3 else ""

                    if name.upper() == "НАИМЕНОВАНИЕ ХАРАКТЕРИСТИКИ":
                        i += 1
                        continue

                    char_type = parse_characteristic_type(instruction)
                    changeable = parse_characteristic_changeable(instruction)

                    characteristic = ItemCharacteristic(
                        id=char_id,
                        name=name,
                        value=value,
                        unit=unit,
                        type=char_type,
                        required=True,
                        changeable=changeable,
                        fillInstruction=instruction if instruction else None
                    )
                    characteristics.append(characteristic)
                    char_id += 1

                i += 1

        # Сохраняем последнюю характеристику если она была
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
                fillInstruction=current_instruction
            )
            characteristics.append(characteristic)

    except Exception as e:
        print(f"Ошибка при парсинге характеристик из таблицы: {e}")

    return characteristics