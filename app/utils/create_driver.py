import logging
import time
from contextlib import contextmanager
from typing import Optional

from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver


logger = logging.getLogger(__name__)

def chrome_options(headless=True) -> Options:
    """Создает Chrome драйвер с настройками для стабильной работы"""
    options = Options()

    # Режим работы
    if headless:
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')

    # Стабильность
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-features=VizDisplayCompositor')

    # Производительность
    options.add_argument('--disable-images')
    options.add_argument('--disable-plugins')
    options.add_argument('--disable-extensions')

    # Размер окна
    options.add_argument('--window-size=1920,1080')

    # Обход защиты от ботов
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # User-Agent
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    # Отключение уведомлений
    prefs = {'profile.default_content_setting_values.notifications': 2}
    options.add_experimental_option('prefs', prefs)

    # Игнорирование SSL ошибок
    options.add_argument('--ignore-certificate-errors')

    # Память
    options.add_argument('--memory-pressure-off')

    return options


@contextmanager
def get_driver(headless: bool = True, page_load_timeout: int = 5):
    """Контекстный менеджер для безопасной работы с драйвером"""
    driver: Optional[WebDriver] = None
    start_time = time.time()

    try:
        logger.info("Создание Chrome драйвера")
        options = chrome_options(headless)
        driver = webdriver.Chrome(options=options)

        # Настройка таймаутов
        driver.set_page_load_timeout(page_load_timeout)

        logger.info(f"Драйвер создан успешно (session_id: {driver.session_id})")
        yield driver

    except WebDriverException as e:
        logger.error(f"Ошибка WebDriver: {e}")
        raise

    except Exception as e:
        logger.error(f"Неожиданная ошибка при создании драйвера: {e}", exc_info=True)
        raise

    finally:
        if driver:
            try:
                # Очистка состояния перед закрытием
                logger.debug("Очистка состояния драйвера")
                driver.delete_all_cookies()

                # Очистка localStorage и sessionStorage только если на странице
                if driver.current_url and driver.current_url != "data:,":
                    try:
                        driver.execute_script("window.localStorage.clear();")
                        driver.execute_script("window.sessionStorage.clear();")
                    except:
                        pass  # Может не работать на некоторых страницах

                # Закрытие драйвера
                logger.info(f"Закрытие драйвера (session_id: {driver.session_id})")
                driver.quit()

                # Логирование времени работы
                duration = time.time() - start_time
                logger.info(f"Сессия драйвера завершена. Продолжительность: {duration:.2f} сек")

            except Exception as e:
                logger.warning(f"Ошибка при закрытии драйвера: {e}")
                # Пытаемся принудительно закрыть
                try:
                    driver.quit()
                except:
                    pass