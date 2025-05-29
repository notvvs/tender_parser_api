import logging
import re
from typing import Optional

from playwright.async_api import Page

from app.utils.format_check import is_paste_format
from app.utils.expand_elements import expand_collapse_blocks

logger = logging.getLogger(__name__)


async def get_delivery_address(page: Page) -> Optional[str]:
    """Главная функция для извлечения адреса доставки"""
    logger.info("Начало извлечения адреса доставки")

    if await is_paste_format(page):
        return await parse_delivery_address_paste(page)
    else:
        return await parse_delivery_address_html(page)


async def parse_delivery_address_paste(page: Page) -> Optional[str]:
    """Извлечение адреса доставки для формата paste"""
    logger.debug("Используется парсер для формата paste")
    await expand_collapse_blocks(page)

    try:
        sections = await page.query_selector_all(
            "div.collapse__content section.blockInfo__section.section"
        )

        logger.debug(f"Найдено {len(sections)} секций в collapse блоках")

        for section in sections:
            try:
                title = await section.query_selector("span.section__title")
                if title:
                    title_text = await title.text_content()
                    if "Место поставки товара" in title_text:
                        info = await section.query_selector("span.section__info")
                        if info:
                            address = await info.text_content()
                            address = re.sub(r"\s+", " ", address.strip())
                            logger.info(f"Найден адрес доставки: {address[:50]}...")
                            return address
            except Exception as e:
                logger.debug(f"Ошибка при обработке секции: {e}")
                continue

        logger.warning("Адрес доставки не найден в формате paste")

    except Exception as e:
        logger.error(f"Ошибка при парсинге адреса (paste): {e}")

    return None


async def parse_delivery_address_html(page: Page) -> Optional[str]:
    """Извлечение адреса доставки для формата html_content"""
    logger.debug("Используется парсер для формата html_content")

    try:
        sections = await page.query_selector_all("section.blockInfo__section.section")
        logger.debug(f"Найдено {len(sections)} секций")

        for section in sections:
            try:
                title = await section.query_selector("span.section__title")
                if title:
                    title_text = await title.text_content()
                    if "Место поставки товара" in title_text:
                        info = await section.query_selector("span.section__info")
                        if info:
                            address = await info.text_content()
                            address = re.sub(r"\s+", " ", address.strip())
                            logger.info(f"Найден адрес доставки: {address[:50]}...")
                            return address
            except Exception as e:
                logger.debug(f"Ошибка при обработке секции: {e}")
                continue

        logger.warning("Адрес доставки не найден в формате html_content")

    except Exception as e:
        logger.error(f"Ошибка при парсинге адреса (html): {e}")

    return None
