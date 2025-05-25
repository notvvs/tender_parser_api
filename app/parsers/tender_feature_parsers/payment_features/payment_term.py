from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
from typing import Optional
import re
import logging

from app.utils.expand_elements import expand_collapse_blocks
from app.utils.format_check import is_paste_format

logger = logging.getLogger(__name__)


def get_payment_term(driver: WebDriver) -> Optional[str]:
    """Главная функция для извлечения срока оплаты"""
    logger.info("Начало извлечения срока оплаты")

    # Проверяем формат и раскрываем блоки если нужно
    if is_paste_format(driver):
        expand_collapse_blocks(driver)
        return parse_payment_term_paste(driver)
    else:
        return parse_payment_term_html(driver)


def parse_payment_term_paste(driver: WebDriver) -> Optional[str]:
    """Извлечение срока оплаты для формата paste"""
    logger.debug("Используется парсер для формата paste")

    try:
        # 1. Ищем прямое указание срока оплаты
        try:
            element = driver.find_element(By.XPATH,
                                          "//div[contains(@class, 'collapse__content')]//section[.//span[@class='section__title'][contains(text(),'Срок оплаты')]]/span[@class='section__info']"
                                          )
            payment_term = element.text.strip()
            logger.info(f"Найден срок оплаты: {payment_term}")
            return payment_term
        except:
            logger.debug("Прямое указание срока оплаты не найдено")

        # 2. Проверяем упоминание об оплате в сроке исполнения контракта
        try:
            elements = driver.find_elements(By.XPATH,
                                            "//div[contains(@class, 'collapse__content')]//span[@class='section__info']"
                                            )
            for element in elements:
                text = element.text.strip()
                if "включает в том числе приемку" in text and "оплату" in text:
                    # Ищем срок исполнения контракта
                    sections = driver.find_elements(By.XPATH,
                                                    "//div[contains(@class, 'collapse__content')]//section[@class='blockInfo__section']"
                                                    )
                    for section in sections:
                        try:
                            title = section.find_element(By.CSS_SELECTOR, "span.section__title")
                            if title.text.strip() == "Срок исполнения контракта":
                                info = section.find_element(By.CSS_SELECTOR, "span.section__info")
                                term = info.text.strip()
                                result = f"В рамках срока исполнения контракта: {term}"
                                logger.info(f"Найден срок оплаты: {result}")
                                return result
                        except:
                            continue
        except Exception as e:
            logger.debug(f"Ошибка при поиске срока в рамках исполнения контракта: {e}")

        # 3. Ищем в условиях оплаты или платежа
        try:
            element = driver.find_element(By.XPATH,
                                          "//div[contains(@class, 'collapse__content')]//section[.//span[@class='section__title'][contains(text(),'Условия оплаты') or contains(text(),'Порядок оплаты')]]/span[@class='section__info']"
                                          )
            payment_conditions = element.text.strip()
            # Извлекаем срок из условий
            term_match = re.search(r'(\d+\s*(дней|дня|день|календарных дней|рабочих дней))', payment_conditions)
            if term_match:
                result = term_match.group(1)
                logger.info(f"Найден срок оплаты из условий: {result}")
                return result
        except:
            logger.debug("Условия оплаты не найдены")

        logger.warning("Срок оплаты не найден в формате paste")
        return None

    except Exception as e:
        logger.error(f"Ошибка при парсинге срока оплаты (paste): {e}")
        return None


def parse_payment_term_html(driver: WebDriver) -> Optional[str]:
    """Извлечение срока оплаты для формата html_content"""
    logger.debug("Используется парсер для формата html_content")

    try:
        # 1. Ищем прямое указание срока оплаты
        try:
            element = driver.find_element(By.XPATH,
                                          "//section[.//span[@class='section__title'][contains(text(),'Срок оплаты')]]/span[@class='section__info']"
                                          )
            payment_term = element.text.strip()
            logger.info(f"Найден срок оплаты: {payment_term}")
            return payment_term
        except:
            logger.debug("Прямое указание срока оплаты не найдено")

        # 2. Проверяем упоминание об оплате в сроке исполнения контракта
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, "span.section__info")
            for element in elements:
                text = element.text.strip()
                if "включает в том числе приемку" in text and "оплату" in text:
                    # Ищем срок исполнения контракта
                    sections = driver.find_elements(By.CSS_SELECTOR, "section.blockInfo__section")
                    for section in sections:
                        try:
                            title = section.find_element(By.CSS_SELECTOR, "span.section__title")
                            if title.text.strip() == "Срок исполнения контракта":
                                info = section.find_element(By.CSS_SELECTOR, "span.section__info")
                                term = info.text.strip()
                                result = f"В рамках срока исполнения контракта: {term}"
                                logger.info(f"Найден срок оплаты: {result}")
                                return result
                        except:
                            continue
        except Exception as e:
            logger.debug(f"Ошибка при поиске срока в рамках исполнения контракта: {e}")

        # 3. Ищем в условиях оплаты
        try:
            element = driver.find_element(By.XPATH,
                                          "//section[.//span[@class='section__title'][contains(text(),'Условия оплаты') or contains(text(),'Порядок оплаты')]]/span[@class='section__info']"
                                          )
            payment_conditions = element.text.strip()
            # Извлекаем срок из условий
            term_match = re.search(r'(\d+\s*(дней|дня|день|календарных дней|рабочих дней))', payment_conditions)
            if term_match:
                result = term_match.group(1)
                logger.info(f"Найден срок оплаты из условий: {result}")
                return result
        except:
            logger.debug("Условия оплаты не найдены")

        logger.warning("Срок оплаты не найден в формате html_content")
        return None

    except Exception as e:
        logger.error(f"Ошибка при парсинге срока оплаты (html): {e}")
        return None