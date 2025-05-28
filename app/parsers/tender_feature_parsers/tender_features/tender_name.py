from playwright.async_api import Page


async def get_tender_name(page: Page) -> str:
    """Извлечение наименования закупки"""
    try:
        element = await page.query_selector(
            "section:has(span:text('Наименование объекта закупки')) span.section__info"
        )
        if element:
            return await element.text_content()
    except:
        pass
    return ""