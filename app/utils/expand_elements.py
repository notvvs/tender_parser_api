import asyncio
import logging

from playwright.async_api import Page

logger = logging.getLogger(__name__)


async def expand_collapse_blocks(page: Page):
    """Раскрытие всех свернутых блоков"""
    try:
        collapse_titles = await page.query_selector_all(
            "div.collapse__title:not(.collapse__title_opened)"
        )

        if collapse_titles:
            logger.info(f"Найдено {len(collapse_titles)} свернутых блоков")

        for i, title in enumerate(collapse_titles):
            try:
                await title.click()
                await asyncio.sleep(0.5)
                logger.debug(f"Раскрыт блок {i + 1}/{len(collapse_titles)}")
            except Exception as e:
                logger.warning(f"Не удалось раскрыть блок {i + 1}: {e}")
                continue
    except Exception as e:
        logger.error(f"Ошибка при раскрытии блоков: {e}")


async def expand_all_documents(page: Page):
    """Раскрывает все скрытые документы"""
    try:
        show_more_buttons = await page.query_selector_all(
            "a:has-text('Показать больше'), a:has-text('Показать все')"
        )

        for button in show_more_buttons:
            try:
                await button.scroll_into_view_if_needed()
                await asyncio.sleep(0.5)
                await button.click()
                await asyncio.sleep(0.5)
            except:
                continue
    except:
        pass
