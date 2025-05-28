from playwright.async_api import Page


async def get_customer_name(page: Page) -> str:
    """Извлечение наименования заказчика"""
    try:
        element = await page.query_selector(
            "section:has(span:text('Организация, осуществляющая размещение')) span.section__info"
        )
        if element:
            return await element.text_content()
    except:
        pass
    return ""
