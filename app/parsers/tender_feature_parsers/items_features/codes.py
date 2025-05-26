import re
from typing import Optional


def extract_okpd2_code(cell_text: str) -> Optional[str]:
    """Извлекает код ОКПД2 из текста ячейки"""
    # ОКПД2 в формате XX.XX.XX.XXX
    match = re.search(r'(\d{2}\.\d{2}\.\d{2}\.\d{3})', cell_text)
    if match:
        return match.group(1)
    return None


def extract_ktru_code(cell_text: str) -> Optional[str]:
    """Извлекает код КТРУ из текста ячейки"""
    # КТРУ в формате XX.XX.XX.XXX-XXXXXXXX
    match = re.search(r'(\d{2}\.\d{2}\.\d{2}\.\d{3}-\d{8})', cell_text)
    if match:
        return match.group(1)
    return None