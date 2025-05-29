from playwright.async_api import Page


async def get_purchase_type(page: Page) -> str:
    """Извлечение способа закупки"""
    try:
        element = await page.query_selector(
            "section:has(span:text('Способ определения поставщика (подрядчика, исполнителя)')) span.section__info"
        )
        if element:
            return await element.text_content()
    except:
        pass
    return "Электронный аукцион"
