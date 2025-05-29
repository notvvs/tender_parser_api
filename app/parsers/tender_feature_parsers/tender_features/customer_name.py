from playwright.async_api import Page

from app.utils.validator import clean_text


async def get_customer_name(page: Page) -> str:
    """Извлечение наименования заказчика"""
    try:
        element = await page.query_selector(
            "section:has(span:text('Организация, осуществляющая размещение')) span.section__info"
        )
        if element:
            text = await element.text_content()
            return clean_text(text)
    except:
        pass
    return ""
