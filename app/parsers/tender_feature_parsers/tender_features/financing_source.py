from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from typing import Optional
import logging

from app.utils.expand_elements import expand_collapse_blocks
from app.utils.format_check import is_paste_format


logger = logging.getLogger(__name__)


def get_financing_source(driver: WebDriver) -> Optional[str]:
    """Главная функция для извлечения источника финансирования"""
    logger.info("Начало извлечения источника финансирования")

    # Проверяем формат и раскрываем блоки если нужно
    if is_paste_format(driver):
        expand_collapse_blocks(driver)
        return parse_financing_source_paste(driver)
    else:
        return parse_financing_source_html(driver)


def parse_financing_source_paste(driver: WebDriver) -> Optional[str]:
    """Извлечение источника финансирования для формата paste"""
    logger.debug("Используется парсер для формата paste")

    try:
        # В paste формате ищем внутри collapse__content -> content__block -> blockInfo

        # 1. Проверяем собственные средства организации
        try:
            element = driver.find_element(By.XPATH,
                                          "//div[contains(@class, 'collapse__content')]//section[.//span[@class='section__title'][contains(text(),'Закупка за счет собственных средств организации')]]/span[@class='section__info']"
                                          )
            if "да" in element.text.lower():
                logger.info("Найден источник: Собственные средства организации")
                return "Собственные средства организации"
        except Exception as e:
            logger.debug(f"Собственные средства не найдены: {e}")

        # 2. Проверяем внебюджетные средства - ищем заголовок таблицы
        try:
            element = driver.find_element(By.XPATH,
                                          "//div[contains(@class, 'collapse__content')]//span[@class='section__title'][contains(text(),'За счет внебюджетных средств')]"
                                          )
            if element:
                logger.info("Найден источник: За счет внебюджетных средств")
                return "За счет внебюджетных средств"
        except Exception as e:
            logger.debug(f"Внебюджетные средства не найдены: {e}")

        # 3. Проверяем бюджетные средства
        try:
            element = driver.find_element(By.XPATH,
                                          "//div[contains(@class, 'collapse__content')]//section[.//span[@class='section__title'][contains(text(),'Закупка за счет бюджетных средств')]]/span[@class='section__info']"
                                          )
            if "да" in element.text.lower():
                # Ищем наименование бюджета
                budget_name = find_budget_name_paste(driver)
                if budget_name:
                    result = f"Бюджетные средства ({budget_name})"
                    logger.info(f"Найден источник: {result}")
                    return result
                else:
                    logger.info("Найден источник: Бюджетные средства")
                    return "Бюджетные средства"
        except Exception as e:
            logger.debug(f"Бюджетные средства не найдены: {e}")

        # 4. Проверяем наличие таблиц с КБК и внебюджетными средствами для смешанного финансирования
        try:
            has_budget = False
            has_extra_budget = False

            # Проверяем наличие таблицы с КБК
            try:
                kbk_table = driver.find_element(By.XPATH,
                                                "//div[contains(@class, 'collapse__content')]//table[.//th[contains(text(),'КБК')]]"
                                                )
                if kbk_table:
                    has_budget = True
                    logger.debug("Найдена таблица с КБК")
            except:
                pass

            # Проверяем наличие заголовка внебюджетных средств
            try:
                extra_budget = driver.find_element(By.XPATH,
                                                   "//div[contains(@class, 'collapse__content')]//span[@class='section__title'][contains(text(),'За счет внебюджетных средств')]"
                                                   )
                if extra_budget:
                    has_extra_budget = True
                    logger.debug("Найден заголовок внебюджетных средств")
            except:
                pass

            if has_budget and has_extra_budget:
                logger.info("Найден источник: Смешанное финансирование (бюджетные и внебюджетные средства)")
                return "Смешанное финансирование (бюджетные и внебюджетные средства)"
        except Exception as e:
            logger.debug(f"Ошибка при проверке смешанного финансирования: {e}")

        logger.warning("Источник финансирования не найден в формате paste")
        return None

    except Exception as e:
        logger.error(f"Ошибка при парсинге источника финансирования (paste): {e}")
        return None


def parse_financing_source_html(driver: WebDriver) -> Optional[str]:
    """Извлечение источника финансирования для формата html_content"""
    logger.debug("Используется парсер для формата html_content")

    try:
        # 1. Проверяем собственные средства организации
        try:
            element = driver.find_element(By.XPATH,
                                          "//section[.//span[@class='section__title'][contains(text(),'Закупка за счет собственных средств организации')]]/span[@class='section__info']"
                                          )
            if "да" in element.text.lower():
                logger.info("Найден источник: Собственные средства организации")
                return "Собственные средства организации"
        except Exception as e:
            logger.debug(f"Собственные средства не найдены: {e}")

        # 2. Проверяем внебюджетные средства
        try:
            element = driver.find_element(By.XPATH,
                                          "//span[@class='section__title'][contains(text(),'За счет внебюджетных средств')]"
                                          )
            if element:
                logger.info("Найден источник: За счет внебюджетных средств")
                return "За счет внебюджетных средств"
        except Exception as e:
            logger.debug(f"Внебюджетные средства не найдены: {e}")

        # 3. Проверяем бюджетные средства
        try:
            element = driver.find_element(By.XPATH,
                                          "//section[.//span[@class='section__title'][contains(text(),'Закупка за счет бюджетных средств')]]/span[@class='section__info']"
                                          )
            if "да" in element.text.lower():
                # Ищем наименование бюджета
                budget_name = find_budget_name_html(driver)
                if budget_name:
                    result = f"Бюджетные средства ({budget_name})"
                    logger.info(f"Найден источник: {result}")
                    return result
                else:
                    logger.info("Найден источник: Бюджетные средства")
                    return "Бюджетные средства"
        except Exception as e:
            logger.debug(f"Бюджетные средства не найдены: {e}")

        # 4. Проверяем смешанное финансирование
        try:
            has_budget = False
            has_extra_budget = False

            # Проверяем наличие таблицы с КБК
            try:
                kbk_table = driver.find_element(By.XPATH,
                                                "//table[.//th[contains(text(),'КБК')]]"
                                                )
                if kbk_table:
                    has_budget = True
            except:
                pass

            # Проверяем наличие заголовка внебюджетных средств
            try:
                extra_budget = driver.find_element(By.XPATH,
                                                   "//span[@class='section__title'][contains(text(),'За счет внебюджетных средств')]"
                                                   )
                if extra_budget:
                    has_extra_budget = True
            except:
                pass

            if has_budget and has_extra_budget:
                logger.info("Найден источник: Смешанное финансирование (бюджетные и внебюджетные средства)")
                return "Смешанное финансирование (бюджетные и внебюджетные средства)"
        except Exception as e:
            logger.debug(f"Ошибка при проверке смешанного финансирования: {e}")

        logger.warning("Источник финансирования не найден в формате html_content")
        return None

    except Exception as e:
        logger.error(f"Ошибка при парсинге источника финансирования (html): {e}")
        return None


def find_budget_name_paste(driver: WebDriver) -> Optional[str]:
    """Поиск наименования бюджета для формата paste"""
    try:
        element = driver.find_element(By.XPATH,
                                      "//div[contains(@class, 'collapse__content')]//section[.//span[@class='section__title'][text()='Наименование бюджета']]/span[@class='section__info']"
                                      )
        budget_name = element.text.strip()
        logger.debug(f"Найдено наименование бюджета: {budget_name}")
        return budget_name
    except Exception as e:
        logger.debug(f"Наименование бюджета не найдено (paste): {e}")

    return None


def find_budget_name_html(driver: WebDriver) -> Optional[str]:
    """Поиск наименования бюджета для формата html_content"""
    try:
        element = driver.find_element(By.XPATH,
                                      "//section[.//span[@class='section__title'][text()='Наименование бюджета']]/span[@class='section__info']"
                                      )
        budget_name = element.text.strip()
        logger.debug(f"Найдено наименование бюджета: {budget_name}")
        return budget_name
    except Exception as e:
        logger.debug(f"Наименование бюджета не найдено (html): {e}")

    return None


