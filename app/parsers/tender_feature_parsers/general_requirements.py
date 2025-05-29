import logging
from typing import Optional

from playwright.async_api import Page

from app.schemas.requirements import GeneralRequirements
from app.utils.format_check import is_paste_format
from app.utils.expand_elements import expand_collapse_blocks

logger = logging.getLogger(__name__)


async def get_general_requirements(page: Page) -> GeneralRequirements:
    """Основная функция для извлечения общих требований"""
    logger.info("Начало извлечения общих требований")

    if await is_paste_format(page):
        return await parse_general_requirements_paste(page)
    else:
        return await parse_general_requirements_html(page)


async def parse_general_requirements_paste(page: Page) -> GeneralRequirements:
    """Извлечение общих требований для формата paste"""
    logger.debug("Используется парсер для формата paste")
    await expand_collapse_blocks(page)

    warranty_requirements = await parse_warranty_requirements_paste(page)

    return GeneralRequirements(
        qualityRequirements=None,
        packagingRequirements=None,
        markingRequirements=None,
        warrantyRequirements=warranty_requirements,
        safetyRequirements=None,
        regulatoryRequirements=None
    )


async def parse_general_requirements_html(page: Page) -> GeneralRequirements:
    """Извлечение общих требований для формата html_content"""
    logger.debug("Используется парсер для формата html_content")

    warranty_requirements = await parse_warranty_requirements_html(page)

    return GeneralRequirements(
        qualityRequirements=None,
        packagingRequirements=None,
        markingRequirements=None,
        warrantyRequirements=warranty_requirements,
        safetyRequirements=None,
        regulatoryRequirements=None
    )


async def parse_warranty_requirements_paste(page: Page) -> Optional[str]:
    """Извлечение гарантийных требований для формата paste"""
    try:
        # Проверяем, есть ли блок с гарантийными требованиями внутри collapse__content
        warranty_block = await page.query_selector(
            "div.collapse__content h2:has-text('Требования к гарантии качества товара')"
        )
        if not warranty_block:
            logger.debug("Блок с гарантийными требованиями не найден в формате paste")
            return None

        warranty_info = []

        # Проверяем, требуется ли гарантия
        warranty_required = await page.query_selector(
            "div.collapse__content section:has(span.section__title:has-text('Требуется гарантия качества')) span.section__info"
        )
        if warranty_required:
            text = await warranty_required.text_content()
            if "да" not in text.lower():
                logger.debug("Гарантия не требуется")
                return None

        # Извлекаем срок гарантии
        warranty_term = await page.query_selector(
            "div.collapse__content section:has(span.section__title:has-text('Срок, на который предоставляется гарантия')) span.section__info"
        )
        if warranty_term:
            text = await warranty_term.text_content()
            if text and text.strip() and text.strip() != "-":
                warranty_info.append(text.strip())

        # Извлекаем требования к гарантийному обслуживанию
        warranty_service = await page.query_selector(
            "div.collapse__content section:has(span.section__title:has-text('Информация о требованиях к гарантийному обслуживанию')) span.section__info"
        )
        if warranty_service:
            text = await warranty_service.text_content()
            if text and text.strip() and text.strip() != "-":
                warranty_info.append(f"Гарантийное обслуживание: {text.strip()}")

        # Извлекаем требования к гарантии производителя
        manufacturer_warranty = await page.query_selector(
            "div.collapse__content section:has(span.section__title:has-text('Требования к гарантии производителя')) span.section__info"
        )
        if manufacturer_warranty:
            text = await manufacturer_warranty.text_content()
            if text and text.strip() and text.strip() != "-":
                warranty_info.append(f"Гарантия производителя: {text.strip()}")

        if warranty_info:
            result = "; ".join(warranty_info)
            logger.info(f"Найдены гарантийные требования (paste): {result[:100]}...")
            return result

        return None

    except Exception as e:
        logger.error(f"Ошибка при извлечении гарантийных требований (paste): {e}")
        return None


async def parse_warranty_requirements_html(page: Page) -> Optional[str]:
    """Извлечение гарантийных требований для формата html_content"""
    try:
        # Проверяем, есть ли блок с гарантийными требованиями
        warranty_block = await page.query_selector("h2:has-text('Требования к гарантии качества товара')")
        if not warranty_block:
            logger.debug("Блок с гарантийными требованиями не найден в формате html_content")
            return None

        warranty_info = []

        # Проверяем, требуется ли гарантия
        warranty_required = await page.query_selector(
            "section:has(span.section__title:has-text('Требуется гарантия качества')) span.section__info"
        )
        if warranty_required:
            text = await warranty_required.text_content()
            if "да" not in text.lower():
                logger.debug("Гарантия не требуется")
                return None

        # Извлекаем срок гарантии
        warranty_term = await page.query_selector(
            "section:has(span.section__title:has-text('Срок, на который предоставляется гарантия')) span.section__info"
        )
        if warranty_term:
            text = await warranty_term.text_content()
            if text and text.strip() and text.strip() != "-":
                warranty_info.append(text.strip())

        # Извлекаем требования к гарантийному обслуживанию
        warranty_service = await page.query_selector(
            "section:has(span.section__title:has-text('Информация о требованиях к гарантийному обслуживанию')) span.section__info"
        )
        if warranty_service:
            text = await warranty_service.text_content()
            if text and text.strip() and text.strip() != "-":
                warranty_info.append(f"Гарантийное обслуживание: {text.strip()}")

        # Извлекаем требования к гарантии производителя
        manufacturer_warranty = await page.query_selector(
            "section:has(span.section__title:has-text('Требования к гарантии производителя')) span.section__info"
        )
        if manufacturer_warranty:
            text = await manufacturer_warranty.text_content()
            if text and text.strip() and text.strip() != "-":
                warranty_info.append(f"Гарантия производителя: {text.strip()}")

        if warranty_info:
            result = "; ".join(warranty_info)
            logger.info(f"Найдены гарантийные требования (html): {result[:100]}...")
            return result

        return None

    except Exception as e:
        logger.error(f"Ошибка при извлечении гарантийных требований (html): {e}")
        return None