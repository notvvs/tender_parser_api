import logging
from typing import Optional

from playwright.async_api import Page

from app.utils.expand_elements import expand_collapse_blocks
from app.utils.format_check import is_paste_format
from app.utils.validator import clean_text

logger = logging.getLogger(__name__)


async def get_delivery_term(page: Page) -> Optional[str]:
    """Главная функция для извлечения срока доставки"""
    logger.info("Начало извлечения срока доставки")

    if await is_paste_format(page):
        return await parse_delivery_term_paste(page)
    else:
        return await parse_delivery_term_html(page)


async def parse_delivery_term_paste(page: Page) -> Optional[str]:
    """Извлечение срока доставки для формата paste"""
    logger.debug("Используется парсер для формата paste")
    await expand_collapse_blocks(page)

    try:
        term_parts = []
        sections = await page.query_selector_all(
            "div.collapse__content section.blockInfo__section"
        )

        for section in sections:
            try:
                title = await section.query_selector("span.section__title")
                if title:
                    title_text = await title.text_content()
                    title_text = title_text.strip()

                    if "Дата начала исполнения контракта" in title_text:
                        info = await section.query_selector("span.section__info")
                        if info:
                            start_text = await info.text_content()
                            term_parts.append(f"Начало: {clean_text(start_text)}")

                    elif title_text == "Срок исполнения контракта":
                        info = await section.query_selector("span.section__info")
                        if info:
                            end_text = await info.text_content()
                            term_parts.append(f"Окончание: {clean_text(end_text)}")
            except:
                continue

        if term_parts:
            result = "; ".join(term_parts)
            logger.info(f"Найден срок доставки: {result}")
            return result

    except Exception as e:
        logger.error(f"Ошибка при парсинге срока (paste): {e}")

    return None


async def parse_delivery_term_html(page: Page) -> Optional[str]:
    """Извлечение срока доставки для формата html_content"""
    logger.debug("Используется парсер для формата html_content")

    try:
        term_parts = []
        sections = await page.query_selector_all("section.blockInfo__section")

        for section in sections:
            try:
                title = await section.query_selector("span.section__title")
                if title:
                    title_text = await title.text_content()
                    title_text = title_text.strip()

                    if "Дата начала исполнения контракта" in title_text:
                        info = await section.query_selector("span.section__info")
                        if info:
                            start_text = await info.text_content()
                            term_parts.append(f"Начало: {clean_text(start_text)}")

                    elif title_text == "Срок исполнения контракта":
                        parent_text = await section.text_content()
                        if "финансирования" not in parent_text:
                            info = await section.query_selector("span.section__info")
                            if info:
                                end_text = await info.text_content()
                                term_parts.append(f"Окончание: {clean_text(end_text)}")
            except:
                continue

        if term_parts:
            result = "; ".join(term_parts)
            logger.info(f"Найден срок доставки: {result}")
            return result

    except Exception as e:
        logger.error(f"Ошибка при парсинге срока (html): {e}")

    return None
