from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

def get_purchase_type(driver: WebDriver) -> str:
    """Извлечение способа закупки"""
    try:
        return driver.find_element(
            By.XPATH,
            "//section[.//span[text()='Способ определения поставщика (подрядчика, исполнителя)']]/span[@class='section__info']"
        ).text
    except:
        return "Электронный аукцион"