import re
from app.schemas.items import Price


def parse_quantity(text: str) -> int:
    """Парсер количества для медицинских товаров"""
    # Убираем все пробелы (включая неразрывные) и заменяем запятую на точку
    text = text.replace('\xa0', '').replace(' ', '').replace(',', '.')
    # Оставляем только цифры и точку
    text = re.sub(r'[^\d.]', '', text)
    try:
        return int(float(text))
    except:
        return 0


def parse_price(text: str) -> Price:
    """Парсер цены для медицинских товаров"""
    # Аналогично количеству
    text = text.replace('\xa0', '').replace(' ', '').replace(',', '.')
    text = re.sub(r'[^\d.]', '', text)
    try:
        amount = float(text)
    except:
        amount = 0.0
    return Price(amount=amount, currency="RUB")


def parse_medical_info(form_dosage_text: str) -> dict:
    """Парсит информацию о форме и дозировке"""
    # Инициализация значений по умолчанию
    form = ""
    dosage = ""

    # Разделяем по запятым
    parts = [p.strip() for p in form_dosage_text.split(',')]

    if len(parts) >= 2:
        # Стандартный формат: "ТАБЛЕТКИ, 2.5 мг"
        form = parts[0]
        dosage = parts[1]
    else:
        # Альтернативный формат - ищем дозировку
        dosage_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(мг|мкг|г|ME|ЕД|ед)', form_dosage_text, re.IGNORECASE)

        if dosage_match:
            dosage = dosage_match.group(0)
            dosage_start = dosage_match.start()
            # Всё до дозировки - это форма
            form = form_dosage_text[:dosage_start].strip()
        else:
            # Если не нашли дозировку, берем весь текст как форму
            form = form_dosage_text

    # Очистка от лишних пробелов
    form = ' '.join(form.split())
    dosage = ' '.join(dosage.split())

    return {
        'form': form,
        'dosage': dosage
    }