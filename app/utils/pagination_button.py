import asyncio

from playwright.async_api import Page
import logging

logger = logging.getLogger(__name__)


async def go_to_next_page(page: Page) -> bool:
    """Переходит на следующую страницу"""
    try:
        paginator = await page.query_selector(
            "div[id*='truPagingContainer'] .paginator"
        )
        if not paginator:
            return False

        next_button = await paginator.query_selector("li.page:not(.disabled) a.next")
        if not next_button:
            logger.info("Достигнута последняя страница")
            return False

        await paginator.scroll_into_view_if_needed()
        await asyncio.sleep(0.5)
        await next_button.click()
        await asyncio.sleep(1)

        logger.info("Перешли на следующую страницу")
        return True

    except Exception as e:
        logger.error(f"Ошибка при переходе на следующую страницу: {e}")
        return False
