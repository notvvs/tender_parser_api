import logging
from typing import Optional

from playwright.async_api import Page

from app.utils.expand_elements import expand_collapse_blocks
from app.utils.format_check import is_paste_format

logger = logging.getLogger(__name__)


async def get_payment_method(page: Page) -> Optional[str]:
    """Главная функция для извлечения способа оплаты"""
    logger.info("Начало извлечения способа оплаты")

    if await is_paste_format(page):
        await expand_collapse_blocks(page)
        return await parse_payment_method_paste(page)
    else:
        return await parse_payment_method_html(page)


async def parse_payment_method_paste(page: Page) -> Optional[str]:
    """Извлечение способа оплаты для формата paste"""
    logger.debug("Используется парсер для формата paste")

    try:
        # 1. Прямое указание способа
        element = await page.query_selector(
            "div.collapse__content section:has(span.section__title:has-text('Способ оплаты'), span.section__title:has-text('Форма оплаты')) span.section__info"
        )
        if element:
            payment_method = await element.text_content()
            logger.info(f"Найден способ оплаты: {payment_method}")
            return payment_method.strip()

        # 2. Ищем в условиях
        element = await page.query_selector(
            "div.collapse__content section:has(span.section__title:has-text('Условия оплаты'), span.section__title:has-text('Порядок оплаты')) span.section__info"
        )
        if element:
            text = await element.text_content()
            text = text.strip().lower()

            if "аванс" in text:
                return "С авансированием"
            elif "предоплат" in text:
                return "С предоплатой"
            elif "по факту" in text or "после поставки" in text:
                return "По факту поставки"
            elif "безналичн" in text:
                return "Безналичный расчет"

        logger.info("Используется способ оплаты по умолчанию")
        return "Безналичный расчет"

    except Exception as e:
        logger.error(f"Ошибка при парсинге способа оплаты (paste): {e}")
        return None


async def parse_payment_method_html(page: Page) -> Optional[str]:
    """Извлечение способа оплаты для формата html_content"""
    logger.debug("Используется парсер для формата html_content")

    try:
        # 1. Прямое указание способа
        element = await page.query_selector(
            "section:has(span.section__title:has-text('Способ оплаты'), span.section__title:has-text('Форма оплаты')) span.section__info"
        )
        if element:
            payment_method = await element.text_content()
            logger.info(f"Найден способ оплаты: {payment_method}")
            return payment_method.strip()

        # 2. Ищем в условиях
        element = await page.query_selector(
            "section:has(span.section__title:has-text('Условия оплаты'), span.section__title:has-text('Порядок оплаты')) span.section__info"
        )
        if element:
            text = await element.text_content()
            text = text.strip().lower()

            if "аванс" in text:
                return "С авансированием"
            elif "предоплат" in text:
                return "С предоплатой"
            elif "по факту" in text or "после поставки" in text:
                return "По факту поставки"
            elif "безналичн" in text:
                return "Безналичный расчет"

        logger.info("Используется способ оплаты по умолчанию")
        return "Безналичный расчет"

    except Exception as e:
        logger.error(f"Ошибка при парсинге способа оплаты (html): {e}")
        return None
