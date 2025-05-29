from playwright.async_api import Page


async def get_tender_number(page: Page) -> str:
    """Извлечение номера закупки"""
    try:
        element = await page.query_selector(
            "span.cardMainInfo__purchaseLink.distancedText a"
        )
        if element:
            text = await element.text_content()
            if "№" in text:
                return text.split("№")[-1].strip()
            return text
    except:
        pass
    return ""
