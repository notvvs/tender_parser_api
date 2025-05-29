from app.schemas.items import Price


def parse_price(price_text: str) -> Price:
    """Парсит текст цены в объект Price"""
    # Удаляем все пробелы и заменяем запятую на точку
    cleaned_price = price_text.replace(" ", "").replace("\xa0", "").replace(",", ".")

    # Извлекаем числовое значение
    try:
        amount = float(cleaned_price)
    except ValueError:
        amount = 0.0

    return Price(amount=amount, currency="RUB")
