from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from typing import Optional
import re
import logging
from app.utils.format_check import is_paste_format
from app.utils.expand_elements import expand_collapse_blocks

logger = logging.getLogger(__name__)


def get_delivery_conditions(driver: WebDriver) -> Optional[str]:
    """Главная функция для извлечения условий доставки"""
    logger.info("Начало извлечения условий доставки")

    # Проверяем формат страницы
    if is_paste_format(driver):
        return parse_delivery_conditions_paste(driver)
    else:
        return parse_delivery_conditions_html(driver)


def parse_delivery_conditions_paste(driver: WebDriver) -> Optional[str]:
    """Извлечение условий доставки для формата paste"""
    logger.debug("Используется парсер для формата paste")

    conditions = []
    expand_collapse_blocks(driver)
    try:
        # 1. Проверяем информацию о сроке исполнения (включает приемку и оплату)
        sections = driver.find_elements(By.CSS_SELECTOR, "div.collapse__content section.blockInfo__section")
        logger.debug(f"Найдено {len(sections)} секций для анализа условий")

        for section in sections:
            try:
                info_spans = section.find_elements(By.CSS_SELECTOR, "span.section__info")
                for info in info_spans:
                    text = info.text.strip()
                    if "включает в том числе приемку" in text:
                        conditions.append("Срок исполнения включает приемку и оплату товара")
                        logger.debug("Найдено условие о сроке исполнения")
                        break
            except Exception as e:
                logger.debug(f"Ошибка при проверке срока исполнения: {e}")
                continue

        # 2. Односторонний отказ от контракта
        sections = driver.find_elements(By.CSS_SELECTOR, "div.collapse__content section.blockInfo__section")
        for section in sections:
            try:
                title = section.find_element(By.CSS_SELECTOR, "span.section__title")
                if "односторонн" in title.text.lower() and "отказ" in title.text.lower():
                    info = section.find_element(By.CSS_SELECTOR, "span.section__info")
                    if "да" in info.text.lower():
                        conditions.append("Предусмотрена возможность одностороннего отказа от исполнения контракта")
                        logger.debug("Найдено условие об одностороннем отказе")
                        break
            except Exception as e:
                logger.debug(f"Ошибка при проверке одностороннего отказа: {e}")
                continue

        # 3. Обеспечение исполнения контракта
        contract_sections = driver.find_elements(By.CSS_SELECTOR, "div.collapse__content section.blockInfo__section")
        for i, section in enumerate(contract_sections):
            try:
                title = section.find_element(By.CSS_SELECTOR, "span.section__title")
                if "Требуется обеспечение исполнения контракта" in title.text:
                    info = section.find_element(By.CSS_SELECTOR, "span.section__info")
                    if "да" in info.text.lower():
                        # Ищем размер обеспечения в следующих секциях
                        for j in range(i + 1, min(i + 3, len(contract_sections))):
                            try:
                                next_title = contract_sections[j].find_element(By.CSS_SELECTOR, "span.section__title")
                                if "Размер обеспечения исполнения контракта" in next_title.text:
                                    size_info = contract_sections[j].find_element(By.CSS_SELECTOR, "span.section__info")
                                    size_text = size_info.text.strip()
                                    # Извлекаем процент
                                    percent_match = re.search(r'(\d+(?:[,.]\d+)?)\s*%', size_text)
                                    if percent_match:
                                        conditions.append(
                                            f"Требуется обеспечение исполнения контракта: {percent_match.group(1)} %")
                                        logger.debug(f"Найдено обеспечение контракта: {percent_match.group(1)}%")
                                    else:
                                        conditions.append("Требуется обеспечение исполнения контракта")
                                        logger.debug("Найдено обеспечение контракта без указания процента")
                                    break
                            except Exception as e:
                                logger.debug(f"Ошибка при поиске размера обеспечения: {e}")
                                continue
                    break
            except Exception as e:
                logger.debug(f"Ошибка при проверке обеспечения контракта: {e}")
                continue

        # 4. Гарантия качества
        guarantee_sections = driver.find_elements(By.CSS_SELECTOR, "div.collapse__content section.blockInfo__section")
        for i, section in enumerate(guarantee_sections):
            try:
                title = section.find_element(By.CSS_SELECTOR, "span.section__title")
                if "Требуется гарантия качества товара" in title.text:
                    info = section.find_element(By.CSS_SELECTOR, "span.section__info")
                    if "да" in info.text.lower():
                        # Ищем срок гарантии в следующих секциях
                        for j in range(i + 1, min(i + 3, len(guarantee_sections))):
                            try:
                                next_title = guarantee_sections[j].find_element(By.CSS_SELECTOR, "span.section__title")
                                if "Срок, на который предоставляется гарантия" in next_title.text:
                                    period_info = guarantee_sections[j].find_element(By.CSS_SELECTOR,
                                                                                     "span.section__info")
                                    period_text = period_info.text.strip()
                                    conditions.append(f"Требуется гарантия качества товара: {period_text}")
                                    logger.debug(f"Найдена гарантия качества: {period_text}")
                                    break
                            except Exception as e:
                                logger.debug(f"Ошибка при поиске срока гарантии: {e}")
                                continue
                        else:
                            conditions.append("Требуется гарантия качества товара")
                            logger.debug("Найдена гарантия качества без указания срока")
                    break
            except Exception as e:
                logger.debug(f"Ошибка при проверке гарантии качества: {e}")
                continue

        if conditions:
            result = "; ".join(conditions)
            logger.info(f"Найдены условия доставки: {len(conditions)} условий")
            return result
        else:
            logger.warning("Условия доставки не найдены")
            return None

    except Exception as e:
        logger.error(f"Ошибка при парсинге условий (paste): {e}")

    return None


def parse_delivery_conditions_html(driver: WebDriver) -> Optional[str]:
    """Извлечение условий доставки для формата html_content"""
    logger.debug("Используется парсер для формата html_content")

    conditions = []

    try:
        # 1. Проверяем информацию о сроке исполнения
        sections = driver.find_elements(By.CSS_SELECTOR, "section.blockInfo__section")
        logger.debug(f"Найдено {len(sections)} секций для анализа условий")

        for section in sections:
            try:
                info_spans = section.find_elements(By.CSS_SELECTOR, "span.section__info")
                for info in info_spans:
                    text = info.text.strip()
                    if "включает в том числе приемку" in text:
                        conditions.append("Срок исполнения включает приемку и оплату товара")
                        logger.debug("Найдено условие о сроке исполнения")
                        break
            except Exception as e:
                logger.debug(f"Ошибка при проверке срока исполнения: {e}")
                continue

        # 2. Односторонний отказ от контракта
        sections = driver.find_elements(By.CSS_SELECTOR, "section.blockInfo__section.section")
        for section in sections:
            try:
                title = section.find_element(By.CSS_SELECTOR, "span.section__title")
                if "односторонн" in title.text.lower() and "отказ" in title.text.lower():
                    info = section.find_element(By.CSS_SELECTOR, "span.section__info")
                    if "да" in info.text.lower():
                        conditions.append("Предусмотрена возможность одностороннего отказа от исполнения контракта")
                        logger.debug("Найдено условие об одностороннем отказе")
            except Exception as e:
                logger.debug(f"Ошибка при проверке одностороннего отказа: {e}")
                continue

        # 3. Обеспечение исполнения контракта
        all_sections = driver.find_elements(By.CSS_SELECTOR, "section.blockInfo__section")
        for i, section in enumerate(all_sections):
            try:
                title = section.find_element(By.CSS_SELECTOR, "span.section__title")
                if "Требуется обеспечение исполнения контракта" in title.text:
                    info = section.find_element(By.CSS_SELECTOR, "span.section__info")
                    if "да" in info.text.lower():
                        # Ищем размер в следующих секциях
                        for j in range(i + 1, min(i + 3, len(all_sections))):
                            try:
                                next_title = all_sections[j].find_element(By.CSS_SELECTOR, "span.section__title")
                                if "Размер обеспечения исполнения контракта" in next_title.text:
                                    size_info = all_sections[j].find_element(By.CSS_SELECTOR, "span.section__info")
                                    size_text = size_info.text.strip()
                                    percent_match = re.search(r'(\d+(?:[,.]\d+)?)\s*%', size_text)
                                    if percent_match:
                                        conditions.append(
                                            f"Требуется обеспечение исполнения контракта: {percent_match.group(1)} %")
                                        logger.debug(f"Найдено обеспечение контракта: {percent_match.group(1)}%")
                                    else:
                                        conditions.append("Требуется обеспечение исполнения контракта")
                                        logger.debug("Найдено обеспечение контракта без указания процента")
                                    break
                            except Exception as e:
                                logger.debug(f"Ошибка при поиске размера обеспечения: {e}")
                                continue
            except Exception as e:
                logger.debug(f"Ошибка при проверке обеспечения контракта: {e}")
                continue

        # 4. Гарантия качества
        guarantee_sections = driver.find_elements(By.CSS_SELECTOR, "section.blockInfo__section")
        for i, section in enumerate(guarantee_sections):
            try:
                title = section.find_element(By.CSS_SELECTOR, "span.section__title")
                if "Требуется гарантия качества товара" in title.text:
                    info = section.find_element(By.CSS_SELECTOR, "span.section__info")
                    if "да" in info.text.lower():
                        # Ищем срок в следующих секциях
                        for j in range(i + 1, min(i + 3, len(guarantee_sections))):
                            try:
                                next_title = guarantee_sections[j].find_element(By.CSS_SELECTOR, "span.section__title")
                                if "Срок, на который предоставляется гарантия" in next_title.text:
                                    period_info = guarantee_sections[j].find_element(By.CSS_SELECTOR,
                                                                                     "span.section__info")
                                    period_text = period_info.text.strip()
                                    conditions.append(f"Требуется гарантия качества товара: {period_text}")
                                    logger.debug(f"Найдена гарантия качества: {period_text}")
                                    break
                            except Exception as e:
                                logger.debug(f"Ошибка при поиске срока гарантии: {e}")
                                continue
                        else:
                            conditions.append("Требуется гарантия качества товара")
                            logger.debug("Найдена гарантия качества без указания срока")
            except Exception as e:
                logger.debug(f"Ошибка при проверке гарантии качества: {e}")
                continue

        if conditions:
            result = "; ".join(conditions)
            logger.info(f"Найдены условия доставки: {len(conditions)} условий")
            return result
        else:
            logger.warning("Условия доставки не найдены")
            return None

    except Exception as e:
        logger.error(f"Ошибка при парсинге условий (html): {e}")

    return None