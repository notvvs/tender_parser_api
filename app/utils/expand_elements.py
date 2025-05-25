from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
import logging

logger = logging.getLogger(__name__)

def expand_collapse_blocks(driver: WebDriver):
    """Раскрытие всех свернутых блоков (для формата paste)"""
    try:
        collapse_titles = driver.find_elements(By.CSS_SELECTOR,
                                               "div.collapse__title:not(.collapse__title_opened)")

        if collapse_titles:
            logger.info(f"Найдено {len(collapse_titles)} свернутых блоков")

        for i, title in enumerate(collapse_titles):
            try:
                driver.execute_script("arguments[0].click();", title)
                import time
                time.sleep(0.5)
                logger.debug(f"Раскрыт блок {i + 1}/{len(collapse_titles)}")
            except Exception as e:
                logger.warning(f"Не удалось раскрыть блок {i + 1}: {e}")
                continue
    except Exception as e:
        logger.error(f"Ошибка при раскрытии блоков: {e}")


def expand_all_documents(driver):
    """Раскрывает все скрытые документы на странице"""
    try:
        # Ищем все кнопки "Показать больше"
        show_more_buttons = driver.find_elements(
            By.XPATH,
            "//a[contains(text(), 'Показать больше') or contains(text(), 'Показать все')]"
        )

        for button in show_more_buttons:
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", button)
                time.sleep(0.5)
            except:
                continue
    except:
        pass