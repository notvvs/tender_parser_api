from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
import logging

logger = logging.getLogger(__name__)


def is_paste_format(driver: WebDriver) -> bool:
    """Проверка формата страницы - paste (с collapse блоками) или html_content"""
    try:
        collapse_blocks = driver.find_elements(By.CSS_SELECTOR, "div.blockInfo__collapse.collapseInfo")
        is_paste = len(collapse_blocks) > 0
        logger.debug(f"Определен формат страницы: {'paste' if is_paste else 'html_content'}")
        return is_paste
    except Exception as e:
        logger.error(f"Ошибка при определении формата страницы: {e}")
        return False


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