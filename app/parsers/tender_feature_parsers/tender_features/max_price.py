import re

from playwright.async_api import Page

from app.schemas.items import Price


async def get_currency(page: Page) -> str:
    """Извлечение валюты"""
    try:
        element = await page.query_selector("span:text('Валюта') ~ span.section__info")
        if element:
            currency_text = await element.text_content()
            return currency_text.strip()
    except:
        pass
    return "RUB"


async def get_max_price(page: Page) -> float:
    """Извлечение максимальной цены контракта"""
    try:
        element = await page.query_selector(
            "section:has(span.section__title:has-text('Начальная (максимальная) цена контракта')) span.section__info"
        )
        if element:
            price_text = await element.text_content()
            price_text = price_text.replace("\u00a0", " ").replace("&nbsp;", " ")
            price_text = re.sub(r"[^\d\s,.]", "", price_text)
            price_text = price_text.replace(" ", "").replace(",", ".")

            if price_text:
                return float(price_text)
    except:
        pass
    return 0.0


async def get_price_info(page: Page) -> Price:
    max_price = await get_max_price(page)
    currency = await get_currency(page)
    return Price(amount=max_price, currency=currency)
