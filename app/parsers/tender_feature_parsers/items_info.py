
from typing import List

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.parsers.tender_feature_parsers.items_features.item import parse_item_from_row
from app.schemas.items import Item

def get_tender_items(driver: WebDriver) -> List[Item]:
    """Основная функция для парсинга товаров тендера"""
    items = []

    try:
        # Ждем загрузки таблицы товаров
        wait = WebDriverWait(driver, 10)
        wait.until(
            EC.presence_of_element_located((By.ID, "positionKTRU"))
        )

        # Находим таблицу с товарами
        table = driver.find_element(
            By.CSS_SELECTOR,
            "#positionKTRU table.tableBlock"
        )

        # Находим все строки товаров (исключаем заголовок и итоги)
        item_rows = table.find_elements(
            By.CSS_SELECTOR,
            "tbody.tableBlock__body > tr.tableBlock__row"
        )

        item_id = 1
        for row in item_rows:
            # Пропускаем строки с информацией о характеристиках
            if "truInfo_" in row.get_attribute("class"):
                continue

            item = parse_item_from_row(driver, row, item_id)
            if item:
                items.append(item)
                item_id += 1

    finally:
        driver.quit()

    return items

