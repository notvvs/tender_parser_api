def parse_quantity(quantity_text: str) -> int:
    """Парсит количество из текста"""
    # Удаляем все пробелы (включая неразрывные) и заменяем запятую на точку
    cleaned = quantity_text.replace(" ", "").replace("\xa0", "").replace("\u00a0", "")
    cleaned = cleaned.replace(",", ".")

    try:
        # Пробуем преобразовать в float, затем в int
        return int(float(cleaned))
    except (ValueError, TypeError):
        return 0