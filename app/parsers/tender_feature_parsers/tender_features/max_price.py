import re

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver

from app.schemas.items import Price



def get_currency(driver: WebDriver) :
    """Извлечение валюты"""
    try:
        currency_element = driver.find_element(
            By.XPATH,
            "//span[text()='Валюта']/following-sibling::span[@class='section__info']"
        )
        currency_text = currency_element.text.strip()
        return currency_text
    except:
        return 'RUB'


def get_max_price(driver: WebDriver):
    """Извлечение максимальной цены контракта"""
    try:
        price_element = driver.find_element(
            By.XPATH,
            "//section[span[@class='section__title'][contains(text(), 'Начальная (максимальная) цена контракта')]]/span[@class='section__info']"
        )
        price_text = price_element.text

        # Очищаем и преобразуем
        price_text = price_text.replace('\u00A0', ' ').replace('&nbsp;', ' ')

        # Убираем все символы кроме цифр, пробелов, запятых и точек
        price_text = re.sub(r'[^\d\s,.]', '', price_text)

        # Убираем все пробелы
        price_text = price_text.replace(' ', '')

        # Заменяем запятую на точку (десятичный разделитель)
        price_text = price_text.replace(',', '.')

        if price_text:
            return float(price_text)
    except:
        pass


def get_price_info(driver: WebDriver) -> Price:

    max_price = get_max_price(driver)
    currency = get_currency(driver)

    return Price(amount=max_price, currency=currency)


