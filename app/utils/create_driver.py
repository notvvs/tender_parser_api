from contextlib import asynccontextmanager
from playwright.async_api import async_playwright, Page


@asynccontextmanager
async def get_page(headless: bool = True):
    """Контекстный менеджер для получения страницы"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=headless,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        page.set_default_timeout(30000)

        try:
            yield page
        finally:
            await context.close()
            await browser.close()