import time

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

import logging

logger = logging.getLogger(__name__)

def go_to_next_page(driver) -> bool:
    """Переходит на следующую страницу если она существует"""
    try:
        # Ищем активный пагинатор
        paginator = driver.find_element(
            By.CSS_SELECTOR,
            "div[id*='truPagingContainer'] .paginator"
        )

        # Ищем кнопку "следующая" которая НЕ отключена
        try:
            next_button = paginator.find_element(
                By.CSS_SELECTOR,
                "li.page:not(.disabled) a.next"
            )

            # Прокручиваем к пагинатору
            driver.execute_script("arguments[0].scrollIntoView(true);", paginator)
            time.sleep(0.5)

            # Кликаем по кнопке
            driver.execute_script("arguments[0].click();", next_button)

            # Ждем обновления таблицы
            time.sleep(1)

            logger.info("Перешли на следующую страницу")
            return True

        except NoSuchElementException:
            # Кнопка следующей страницы не найдена или отключена
            logger.info("Достигнута последняя страница")
            return False

    except Exception as e:
        logger.error(f"Ошибка при переходе на следующую страницу: {e}")
        return False