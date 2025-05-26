from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
from typing import Optional
import logging
from app.utils.format_check import is_paste_format
from app.utils.expand_elements import expand_collapse_blocks

logger = logging.getLogger(__name__)


def get_delivery_term(driver: WebDriver) -> Optional[str]:
    """Главная функция для извлечения срока доставки"""
    logger.info("Начало извлечения срока доставки")

    # Проверяем формат страницы
    if is_paste_format(driver):
        return parse_delivery_term_paste(driver)
    else:
        return parse_delivery_term_html(driver)


def parse_delivery_term_paste(driver: WebDriver) -> Optional[str]:
    """Извлечение срока доставки для формата paste"""
    logger.debug("Используется парсер для формата paste")
    expand_collapse_blocks(driver)
    try:
        term_parts = []

        # Ищем секции внутри collapse контента
        sections = driver.find_elements(By.CSS_SELECTOR,
                                        "div.collapse__content section.blockInfo__section")

        logger.debug(f"Найдено {len(sections)} секций в collapse блоках")

        for section in sections:
            try:
                title = section.find_element(By.CSS_SELECTOR, "span.section__title")
                title_text = title.text.strip()

                if "Дата начала исполнения контракта" in title_text:
                    info = section.find_element(By.CSS_SELECTOR, "span.section__info")
                    start_text = info.text.strip()
                    term_parts.append(f"Начало: {start_text}")
                    logger.debug(f"Найдена дата начала: {start_text}")

                elif title_text == "Срок исполнения контракта":
                    info = section.find_element(By.CSS_SELECTOR, "span.section__info")
                    end_text = info.text.strip()
                    term_parts.append(f"Окончание: {end_text}")
                    logger.debug(f"Найден срок окончания: {end_text}")
            except Exception as e:
                logger.debug(f"Ошибка при обработке секции: {e}")
                continue

        if term_parts:
            result = "; ".join(term_parts)
            logger.info(f"Найден срок доставки: {result}")
            return result
        else:
            logger.warning("Срок доставки не найден в формате paste")
            return None

    except Exception as e:
        logger.error(f"Ошибка при парсинге срока (paste): {e}")

    return None


def parse_delivery_term_html(driver: WebDriver) -> Optional[str]:
    """Извлечение срока доставки для формата html_content"""
    logger.debug("Используется парсер для формата html_content")

    try:
        term_parts = []

        # Ищем все секции в контейнере
        sections = driver.find_elements(By.CSS_SELECTOR, "section.blockInfo__section")

        logger.debug(f"Найдено {len(sections)} секций")

        for section in sections:
            try:
                # Проверяем наличие заголовка
                titles = section.find_elements(By.CSS_SELECTOR, "span.section__title")
                if not titles:
                    continue

                title = titles[0]
                title_text = title.text.strip()

                # Дата начала исполнения контракта
                if "Дата начала исполнения контракта" in title_text:
                    infos = section.find_elements(By.CSS_SELECTOR, "span.section__info")
                    if infos:
                        start_text = infos[0].text.strip()
                        if start_text:
                            term_parts.append(f"Начало: {start_text}")
                            logger.debug(f"Найдена дата начала: {start_text}")

                # Срок исполнения контракта
                elif title_text == "Срок исполнения контракта":
                    # Проверяем, что это не секция о финансировании
                    parent_text = section.text
                    if "финансирования" not in parent_text:
                        infos = section.find_elements(By.CSS_SELECTOR, "span.section__info")
                        if infos:
                            end_text = infos[0].text.strip()
                            if end_text:
                                term_parts.append(f"Окончание: {end_text}")
                                logger.debug(f"Найден срок окончания: {end_text}")

            except Exception as e:
                logger.debug(f"Ошибка при обработке секции: {e}")
                continue

        if term_parts:
            result = "; ".join(term_parts)
            logger.info(f"Найден срок доставки: {result}")
            return result
        else:
            logger.warning("Срок доставки не найден в формате html_content")
            return None

    except Exception as e:
        logger.error(f"Ошибка при парсинге срока (html): {e}")

    return None