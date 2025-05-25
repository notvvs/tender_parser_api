from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
from typing import Optional
import re
import logging
from app.utils.format_check import is_paste_format, expand_collapse_blocks

logger = logging.getLogger(__name__)


def get_delivery_address(driver: WebDriver) -> Optional[str]:
    """Главная функция для извлечения адреса доставки"""
    logger.info("Начало извлечения адреса доставки")

    # Проверяем формат страницы
    if is_paste_format(driver):
        return parse_delivery_address_paste(driver)
    else:
        return parse_delivery_address_html(driver)


def parse_delivery_address_paste(driver: WebDriver) -> Optional[str]:
    """Извлечение адреса доставки для формата paste"""
    logger.debug("Используется парсер для формата paste")
    expand_collapse_blocks(driver)
    try:
        # В paste формате адрес находится внутри collapse блока
        sections = driver.find_elements(By.CSS_SELECTOR,
                                        "div.collapse__content section.blockInfo__section.section")

        logger.debug(f"Найдено {len(sections)} секций в collapse блоках")

        for section in sections:
            try:
                title = section.find_element(By.CSS_SELECTOR, "span.section__title")
                if "Место поставки товара" in title.text:
                    info = section.find_element(By.CSS_SELECTOR, "span.section__info")
                    address = info.text.strip()
                    # Очищаем от множественных пробелов
                    address = re.sub(r'\s+', ' ', address)
                    logger.info(f"Найден адрес доставки: {address[:50]}...")
                    return address
            except Exception as e:
                logger.debug(f"Ошибка при обработке секции: {e}")
                continue

        logger.warning("Адрес доставки не найден в формате paste")

    except Exception as e:
        logger.error(f"Ошибка при парсинге адреса (paste): {e}")

    return None


def parse_delivery_address_html(driver: WebDriver) -> Optional[str]:
    """Извлечение адреса доставки для формата html_content"""
    logger.debug("Используется парсер для формата html_content")

    try:
        # В html_content формате адрес находится в обычных секциях
        sections = driver.find_elements(By.CSS_SELECTOR, "section.blockInfo__section.section")

        logger.debug(f"Найдено {len(sections)} секций")

        for section in sections:
            try:
                title = section.find_element(By.CSS_SELECTOR, "span.section__title")
                if "Место поставки товара" in title.text:
                    info = section.find_element(By.CSS_SELECTOR, "span.section__info")
                    address = info.text.strip()
                    address = re.sub(r'\s+', ' ', address)
                    logger.info(f"Найден адрес доставки: {address[:50]}...")
                    return address
            except Exception as e:
                logger.debug(f"Ошибка при обработке секции: {e}")
                continue

        logger.warning("Адрес доставки не найден в формате html_content")

    except Exception as e:
        logger.error(f"Ошибка при парсинге адреса (html): {e}")

    return None