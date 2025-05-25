from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
from typing import Optional
import re
import logging

from app.utils.format_check import is_paste_format, expand_collapse_blocks

logger = logging.getLogger(__name__)


def get_payment_conditions(driver: WebDriver) -> Optional[str]:
    """Главная функция для извлечения платежных реквизитов"""
    logger.info("Начало извлечения платежных реквизитов")

    # Проверяем формат и раскрываем блоки если нужно
    if is_paste_format(driver):
        expand_collapse_blocks(driver)
        return parse_payment_conditions_paste(driver)
    else:
        return parse_payment_conditions_html(driver)


def parse_payment_conditions_paste(driver: WebDriver) -> Optional[str]:
    """Извлечение платежных реквизитов для формата paste"""
    logger.debug("Используется парсер для формата paste")

    try:
        # 1. Ищем платежные реквизиты для оплаты
        try:
            element = driver.find_element(By.XPATH,
                                          "//div[contains(@class, 'collapse__content')]//section[.//span[@class='section__title'][contains(text(),'Платежные реквизиты') and not(contains(text(),'обеспечения'))]]/span[@class='section__info']"
                                          )
            requisites = element.text.strip()
            logger.info(f"Найдены платежные реквизиты: {requisites[:50]}...")
            return requisites
        except:
            logger.debug("Платежные реквизиты для оплаты не найдены")

        # 2. Ищем банковские реквизиты
        try:
            element = driver.find_element(By.XPATH,
                                          "//div[contains(@class, 'collapse__content')]//section[.//span[@class='section__title'][contains(text(),'Банковские реквизиты') or contains(text(),'Реквизиты счета')]]/span[@class='section__info']"
                                          )
            requisites = element.text.strip()
            logger.info(f"Найдены банковские реквизиты: {requisites[:50]}...")
            return requisites
        except:
            logger.debug("Банковские реквизиты не найдены")

        # 3. Используем реквизиты для обеспечения контракта как fallback
        try:
            element = driver.find_element(By.XPATH,
                                          "//div[contains(@class, 'collapse__content')]//section[.//span[@class='section__title'][contains(text(),'Платежные реквизиты для обеспечения исполнения контракта')]]/span[@class='section__info']"
                                          )
            requisites = element.text.strip()
            # Очищаем от множественных пробелов
            requisites = re.sub(r'\s+', ' ', requisites)
            logger.info(f"Найдены реквизиты для обеспечения (используются как основные): {requisites[:50]}...")
            return requisites
        except:
            logger.debug("Реквизиты для обеспечения контракта не найдены")

        # 4. Ищем реквизиты счета для учета операций
        try:
            element = driver.find_element(By.XPATH,
                                          "//div[contains(@class, 'collapse__content')]//section[.//span[@class='section__title'][contains(text(),'Реквизиты счета для учета операций')]]/span[@class='section__info']"
                                          )
            requisites = element.text.strip()
            requisites = re.sub(r'\s+', ' ', requisites)
            logger.info(f"Найдены реквизиты счета: {requisites[:50]}...")
            return requisites
        except:
            logger.debug("Реквизиты счета не найдены")

        logger.warning("Платежные реквизиты не найдены в формате paste")
        return None

    except Exception as e:
        logger.error(f"Ошибка при парсинге платежных реквизитов (paste): {e}")
        return None


def parse_payment_conditions_html(driver: WebDriver) -> Optional[str]:
    """Извлечение платежных реквизитов для формата html_content"""
    logger.debug("Используется парсер для формата html_content")

    try:
        # 1. Ищем платежные реквизиты для оплаты
        try:
            element = driver.find_element(By.XPATH,
                                          "//section[.//span[@class='section__title'][contains(text(),'Платежные реквизиты') and not(contains(text(),'обеспечения'))]]/span[@class='section__info']"
                                          )
            requisites = element.text.strip()
            logger.info(f"Найдены платежные реквизиты: {requisites[:50]}...")
            return requisites
        except:
            logger.debug("Платежные реквизиты для оплаты не найдены")

        # 2. Ищем банковские реквизиты
        try:
            element = driver.find_element(By.XPATH,
                                          "//section[.//span[@class='section__title'][contains(text(),'Банковские реквизиты') or contains(text(),'Реквизиты счета')]]/span[@class='section__info']"
                                          )
            requisites = element.text.strip()
            logger.info(f"Найдены банковские реквизиты: {requisites[:50]}...")
            return requisites
        except:
            logger.debug("Банковские реквизиты не найдены")

        # 3. Используем реквизиты для обеспечения контракта как fallback
        try:
            element = driver.find_element(By.XPATH,
                                          "//section[.//span[@class='section__title'][contains(text(),'Платежные реквизиты для обеспечения исполнения контракта')]]/span[@class='section__info']"
                                          )
            requisites = element.text.strip()
            # Очищаем от множественных пробелов
            requisites = re.sub(r'\s+', ' ', requisites)
            logger.info(f"Найдены реквизиты для обеспечения (используются как основные): {requisites[:50]}...")
            return requisites
        except:
            logger.debug("Реквизиты для обеспечения контракта не найдены")

        # 4. Ищем реквизиты счета для учета операций
        try:
            element = driver.find_element(By.XPATH,
                                          "//section[.//span[@class='section__title'][contains(text(),'Реквизиты счета для учета операций')]]/span[@class='section__info']"
                                          )
            requisites = element.text.strip()
            requisites = re.sub(r'\s+', ' ', requisites)
            logger.info(f"Найдены реквизиты счета: {requisites[:50]}...")
            return requisites
        except:
            logger.debug("Реквизиты счета не найдены")

        logger.warning("Платежные реквизиты не найдены в формате html_content")
        return None

    except Exception as e:
        logger.error(f"Ошибка при парсинге платежных реквизитов (html): {e}")
        return None