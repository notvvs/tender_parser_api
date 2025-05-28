from typing import Optional

from playwright.async_api import Page

from app.utils.format_check import is_paste_format
from app.utils.expand_elements import expand_collapse_blocks
import logging

logger = logging.getLogger(__name__)

async def get_financing_source(page: Page) -> Optional[str]:
    """Главная функция для извлечения источника финансирования"""
    logger.info("Начало извлечения источника финансирования")

    if await is_paste_format(page):
        await expand_collapse_blocks(page)
        return await parse_financing_source_paste(page)
    else:
        return await parse_financing_source_html(page)


async def parse_financing_source_paste(page: Page) -> Optional[str]:
    """Извлечение источника финансирования для формата paste"""
    logger.debug("Используется парсер для формата paste")

    try:
        # 1. Проверяем собственные средства
        element = await page.query_selector(
            "div.collapse__content section:has(span.section__title:has-text('Закупка за счет собственных средств организации')) span.section__info"
        )
        if element:
            text = await element.text_content()
            if "да" in text.lower():
                logger.info("Найден источник: Собственные средства организации")
                return "Собственные средства организации"

        # 2. Проверяем внебюджетные средства
        element = await page.query_selector(
            "div.collapse__content span.section__title:has-text('За счет внебюджетных средств')"
        )
        if element:
            logger.info("Найден источник: За счет внебюджетных средств")
            return "За счет внебюджетных средств"

        # 3. Проверяем бюджетные средства
        element = await page.query_selector(
            "div.collapse__content section:has(span.section__title:has-text('Закупка за счет бюджетных средств')) span.section__info"
        )
        if element:
            text = await element.text_content()
            if "да" in text.lower():
                budget_name = await find_budget_name_paste(page)
                if budget_name:
                    result = f"Бюджетные средства ({budget_name})"
                    logger.info(f"Найден источник: {result}")
                    return result
                else:
                    logger.info("Найден источник: Бюджетные средства")
                    return "Бюджетные средства"

        logger.warning("Источник финансирования не найден в формате paste")
        return None

    except Exception as e:
        logger.error(f"Ошибка при парсинге источника финансирования (paste): {e}")
        return None


async def parse_financing_source_html(page: Page) -> Optional[str]:
    """Извлечение источника финансирования для формата html_content"""
    logger.debug("Используется парсер для формата html_content")

    try:
        # 1. Проверяем собственные средства
        element = await page.query_selector(
            "section:has(span.section__title:has-text('Закупка за счет собственных средств организации')) span.section__info"
        )
        if element:
            text = await element.text_content()
            if "да" in text.lower():
                logger.info("Найден источник: Собственные средства организации")
                return "Собственные средства организации"

        # 2. Проверяем внебюджетные средства
        element = await page.query_selector(
            "span.section__title:has-text('За счет внебюджетных средств')"
        )
        if element:
            logger.info("Найден источник: За счет внебюджетных средств")
            return "За счет внебюджетных средств"

        # 3. Проверяем бюджетные средства
        element = await page.query_selector(
            "section:has(span.section__title:has-text('Закупка за счет бюджетных средств')) span.section__info"
        )
        if element:
            text = await element.text_content()
            if "да" in text.lower():
                budget_name = await find_budget_name_html(page)
                if budget_name:
                    result = f"Бюджетные средства ({budget_name})"
                    logger.info(f"Найден источник: {result}")
                    return result
                else:
                    logger.info("Найден источник: Бюджетные средства")
                    return "Бюджетные средства"

        logger.warning("Источник финансирования не найден в формате html_content")
        return None

    except Exception as e:
        logger.error(f"Ошибка при парсинге источника финансирования (html): {e}")
        return None


async def find_budget_name_paste(page: Page) -> Optional[str]:
    """Поиск наименования бюджета для формата paste"""
    try:
        element = await page.query_selector(
            "div.collapse__content section:has(span.section__title:text('Наименование бюджета')) span.section__info"
        )
        if element:
            budget_name = await element.text_content()
            logger.debug(f"Найдено наименование бюджета: {budget_name}")
            return budget_name.strip()
    except Exception as e:
        logger.debug(f"Наименование бюджета не найдено (paste): {e}")
    return None


async def find_budget_name_html(page: Page) -> Optional[str]:
    """Поиск наименования бюджета для формата html_content"""
    try:
        element = await page.query_selector(
            "section:has(span.section__title:text('Наименование бюджета')) span.section__info"
        )
        if element:
            budget_name = await element.text_content()
            logger.debug(f"Найдено наименование бюджета: {budget_name}")
            return budget_name.strip()
    except Exception as e:
        logger.debug(f"Наименование бюджета не найдено (html): {e}")
    return None