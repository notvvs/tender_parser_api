import logging
import re
from typing import Optional

from playwright.async_api import Page

from app.utils.expand_elements import expand_collapse_blocks
from app.utils.format_check import is_paste_format

logger = logging.getLogger(__name__)


async def get_payment_conditions(page: Page) -> Optional[str]:
    """Главная функция для извлечения платежных реквизитов"""
    logger.info("Начало извлечения платежных реквизитов")

    if await is_paste_format(page):
        await expand_collapse_blocks(page)
        return await parse_payment_conditions_paste(page)
    else:
        return await parse_payment_conditions_html(page)


async def parse_payment_conditions_paste(page: Page) -> Optional[str]:
    """Извлечение платежных реквизитов для формата paste"""
    logger.debug("Используется парсер для формата paste")

    try:
        # 1. Платежные реквизиты
        element = await page.query_selector(
            "div.collapse__content section:has(span.section__title:has-text('Платежные реквизиты'):not(:has-text('обеспечения'))) span.section__info"
        )
        if element:
            requisites = await element.text_content()
            logger.info(f"Найдены платежные реквизиты: {requisites[:50]}...")
            return requisites.strip()

        # 2. Банковские реквизиты
        element = await page.query_selector(
            "div.collapse__content section:has(span.section__title:has-text('Банковские реквизиты'), span.section__title:has-text('Реквизиты счета')) span.section__info"
        )
        if element:
            requisites = await element.text_content()
            logger.info(f"Найдены банковские реквизиты: {requisites[:50]}...")
            return requisites.strip()

        # 3. Реквизиты для обеспечения как fallback
        element = await page.query_selector(
            "div.collapse__content section:has(span.section__title:has-text('Платежные реквизиты для обеспечения исполнения контракта')) span.section__info"
        )
        if element:
            requisites = await element.text_content()
            requisites = re.sub(r"\s+", " ", requisites.strip())
            logger.info(f"Найдены реквизиты для обеспечения: {requisites[:50]}...")
            return requisites

        logger.warning("Платежные реквизиты не найдены в формате paste")
        return None

    except Exception as e:
        logger.error(f"Ошибка при парсинге платежных реквизитов (paste): {e}")
        return None


async def parse_payment_conditions_html(page: Page) -> Optional[str]:
    """Извлечение платежных реквизитов для формата html_content"""
    logger.debug("Используется парсер для формата html_content")

    try:
        # 1. Платежные реквизиты
        element = await page.query_selector(
            "section:has(span.section__title:has-text('Платежные реквизиты'):not(:has-text('обеспечения'))) span.section__info"
        )
        if element:
            requisites = await element.text_content()
            logger.info(f"Найдены платежные реквизиты: {requisites[:50]}...")
            return requisites.strip()

        # 2. Банковские реквизиты
        element = await page.query_selector(
            "section:has(span.section__title:has-text('Банковские реквизиты'), span.section__title:has-text('Реквизиты счета')) span.section__info"
        )
        if element:
            requisites = await element.text_content()
            logger.info(f"Найдены банковские реквизиты: {requisites[:50]}...")
            return requisites.strip()

        # 3. Реквизиты для обеспечения как fallback
        element = await page.query_selector(
            "section:has(span.section__title:has-text('Платежные реквизиты для обеспечения исполнения контракта')) span.section__info"
        )
        if element:
            requisites = await element.text_content()
            requisites = re.sub(r"\s+", " ", requisites.strip())
            logger.info(f"Найдены реквизиты для обеспечения: {requisites[:50]}...")
            return requisites

        logger.warning("Платежные реквизиты не найдены в формате html_content")
        return None

    except Exception as e:
        logger.error(f"Ошибка при парсинге платежных реквизитов (html): {e}")
        return None
