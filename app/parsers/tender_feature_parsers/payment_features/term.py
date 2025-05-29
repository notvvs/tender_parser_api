import logging
from typing import Optional

from playwright.async_api import Page

from app.utils.expand_elements import expand_collapse_blocks
from app.utils.format_check import is_paste_format
from app.utils.validator import clean_text

logger = logging.getLogger(__name__)


async def get_payment_term(page: Page) -> Optional[str]:
    """Главная функция для извлечения срока оплаты"""
    logger.info("Начало извлечения срока оплаты")

    if await is_paste_format(page):
        await expand_collapse_blocks(page)
        return await parse_payment_term_paste(page)
    else:
        return await parse_payment_term_html(page)


async def parse_payment_term_paste(page: Page) -> Optional[str]:
    """Извлечение срока оплаты для формата paste"""
    logger.debug("Используется парсер для формата paste")

    try:
        # 1. Прямое указание срока оплаты
        element = await page.query_selector(
            "div.collapse__content section:has(span.section__title:has-text('Срок оплаты')) span.section__info"
        )
        if element:
            payment_term = await element.text_content()
            logger.info(f"Найден срок оплаты: {payment_term}")
            return payment_term

        # 2. Проверяем упоминание в сроке исполнения
        elements = await page.query_selector_all(
            "div.collapse__content span.section__info"
        )
        for element in elements:
            text = await element.text_content()
            if "включает в том числе приемку" in text and "оплату" in text:
                sections = await page.query_selector_all(
                    "div.collapse__content section.blockInfo__section"
                )
                for section in sections:
                    try:
                        title = await section.query_selector("span.section__title")
                        if title:
                            title_text = await title.text_content()
                            if title_text.strip() == "Срок исполнения контракта":
                                info = await section.query_selector(
                                    "span.section__info"
                                )
                                if info:
                                    term = await info.text_content()
                                    result = f"В рамках срока исполнения контракта: {clean_text(term)}"
                                    logger.info(f"Найден срок оплаты: {result}")
                                    return result
                    except:
                        continue

        logger.warning("Срок оплаты не найден в формате paste")
        return None

    except Exception as e:
        logger.error(f"Ошибка при парсинге срока оплаты (paste): {e}")
        return None


async def parse_payment_term_html(page: Page) -> Optional[str]:
    """Извлечение срока оплаты для формата html_content"""
    logger.debug("Используется парсер для формата html_content")

    try:
        # 1. Прямое указание срока оплаты
        element = await page.query_selector(
            "section:has(span.section__title:has-text('Срок оплаты')) span.section__info"
        )
        if element:
            payment_term = await element.text_content()
            logger.info(f"Найден срок оплаты: {payment_term}")
            return payment_term

        # 2. Проверяем упоминание в сроке исполнения
        elements = await page.query_selector_all("span.section__info")
        for element in elements:
            text = await element.text_content()
            if "включает в том числе приемку" in text and "оплату" in text:
                sections = await page.query_selector_all("section.blockInfo__section")
                for section in sections:
                    try:
                        title = await section.query_selector("span.section__title")
                        if title:
                            title_text = await title.text_content()
                            if title_text.strip() == "Срок исполнения контракта":
                                info = await section.query_selector(
                                    "span.section__info"
                                )
                                if info:
                                    term = await info.text_content()
                                    result = f"В рамках срока исполнения контракта: {clean_text(term)}"
                                    logger.info(f"Найден срок оплаты: {result}")
                                    return result
                    except:
                        continue

        logger.warning("Срок оплаты не найден в формате html_content")
        return None

    except Exception as e:
        logger.error(f"Ошибка при парсинге срока оплаты (html): {e}")
        return None
