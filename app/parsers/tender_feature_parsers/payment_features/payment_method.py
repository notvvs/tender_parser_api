from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
from typing import Optional
import logging

from app.utils.format_check import expand_collapse_blocks, is_paste_format

logger = logging.getLogger(__name__)


def get_payment_method(driver: WebDriver) -> Optional[str]:
    """Главная функция для извлечения способа оплаты"""
    logger.info("Начало извлечения способа оплаты")

    # Проверяем формат и раскрываем блоки если нужно
    if is_paste_format(driver):
        expand_collapse_blocks(driver)
        return parse_payment_method_paste(driver)
    else:
        return parse_payment_method_html(driver)


def parse_payment_method_paste(driver: WebDriver) -> Optional[str]:
    """Извлечение способа оплаты для формата paste"""
    logger.debug("Используется парсер для формата paste")

    try:
        # 1. Ищем прямое указание способа оплаты
        try:
            element = driver.find_element(By.XPATH,
                                          "//div[contains(@class, 'collapse__content')]//section[.//span[@class='section__title'][contains(text(),'Способ оплаты') or contains(text(),'Форма оплаты')]]/span[@class='section__info']"
                                          )
            payment_method = element.text.strip()
            logger.info(f"Найден способ оплаты: {payment_method}")
            return payment_method
        except:
            logger.debug("Прямое указание способа оплаты не найдено")

        # 2. Ищем в условиях оплаты
        try:
            element = driver.find_element(By.XPATH,
                                          "//div[contains(@class, 'collapse__content')]//section[.//span[@class='section__title'][contains(text(),'Условия оплаты') or contains(text(),'Порядок оплаты')]]/span[@class='section__info']"
                                          )
            text = element.text.strip().lower()

            # Определяем способ оплаты по ключевым словам
            if "аванс" in text:
                return "С авансированием"
            elif "предоплат" in text:
                return "С предоплатой"
            elif "по факту" in text or "после поставки" in text:
                return "По факту поставки"
            elif "безналичн" in text:
                return "Безналичный расчет"
            else:
                logger.debug(f"Способ оплаты не определен из условий: {text[:100]}...")
        except:
            logger.debug("Условия оплаты для определения способа не найдены")

        # 3. По умолчанию для госконтрактов
        logger.info("Используется способ оплаты по умолчанию")
        return "Безналичный расчет"

    except Exception as e:
        logger.error(f"Ошибка при парсинге способа оплаты (paste): {e}")
        return None


def parse_payment_method_html(driver: WebDriver) -> Optional[str]:
    """Извлечение способа оплаты для формата html_content"""
    logger.debug("Используется парсер для формата html_content")

    try:
        # 1. Ищем прямое указание способа оплаты
        try:
            element = driver.find_element(By.XPATH,
                                          "//section[.//span[@class='section__title'][contains(text(),'Способ оплаты') or contains(text(),'Форма оплаты')]]/span[@class='section__info']"
                                          )
            payment_method = element.text.strip()
            logger.info(f"Найден способ оплаты: {payment_method}")
            return payment_method
        except:
            logger.debug("Прямое указание способа оплаты не найдено")

        # 2. Ищем в условиях оплаты
        try:
            element = driver.find_element(By.XPATH,
                                          "//section[.//span[@class='section__title'][contains(text(),'Условия оплаты') or contains(text(),'Порядок оплаты')]]/span[@class='section__info']"
                                          )
            text = element.text.strip().lower()

            # Определяем способ оплаты по ключевым словам
            if "аванс" in text:
                return "С авансированием"
            elif "предоплат" in text:
                return "С предоплатой"
            elif "по факту" in text or "после поставки" in text:
                return "По факту поставки"
            elif "безналичн" in text:
                return "Безналичный расчет"
            else:
                logger.debug(f"Способ оплаты не определен из условий: {text[:100]}...")
        except:
            logger.debug("Условия оплаты для определения способа не найдены")

        # 3. По умолчанию для госконтрактов
        logger.info("Используется способ оплаты по умолчанию")
        return "Безналичный расчет"

    except Exception as e:
        logger.error(f"Ошибка при парсинге способа оплаты (html): {e}")
        return None