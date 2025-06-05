def parse_quantity(quantity_text: str) -> int:
    """Парсит количество из текста"""
    # Удаляем пробелы и запятые
    cleaned = quantity_text.replace(" ", "").replace(",", ".")

    try:
        # Пробуем преобразовать в float, затем в int
        return int(float(cleaned))
    except ValueError:
        return 0
