import re
from typing import Optional, Tuple
from urllib.parse import urlparse, parse_qs


def validate_tender_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Простая валидация URL тендера с zakupki.gov.ru

    Returns:
        (is_valid, error_message)
    """

    # Базовая проверка на пустоту
    if not url or not url.strip():
        return False, "URL не может быть пустым"

    # Парсим URL
    try:
        parsed = urlparse(url)
    except Exception:
        return False, "Некорректный формат URL"

    # Проверяем домен
    if 'zakupki.gov.ru' not in parsed.netloc:
        return False, f"URL должен быть с сайта zakupki.gov.ru"

    # Проверяем наличие regNumber в параметрах
    query_params = parse_qs(parsed.query)
    reg_number = query_params.get('regNumber', [None])[0]

    if not reg_number:
        return False, "В URL отсутствует параметр regNumber"

    return True, None


def extract_reg_number(url: str) -> Optional[str]:
    """Извлекает regNumber из URL"""
    try:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        return query_params.get('regNumber', [None])[0]
    except:
        return None


def clean_text(text: str) -> str:
    """Очистка текста с сохранением кавычек"""
    if not text:
        return ""

    # Заменяем спецсимволы
    text = text.replace('\xa0', ' ')
    text = text.replace('&nbsp;', ' ')
    text = text.replace('\n', ' ')
    text = text.replace('\r', ' ')
    text = text.replace('\t', ' ')

    # Убираем множественные пробелы
    text = re.sub(r'\s+', ' ', text)

    # Trim
    return text.strip()