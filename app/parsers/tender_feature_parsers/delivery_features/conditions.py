import logging
import re
from typing import Optional

from playwright.async_api import Page

from app.utils.expand_elements import expand_collapse_blocks
from app.utils.format_check import is_paste_format

logger = logging.getLogger(__name__)

async def get_delivery_conditions(page: Page) -> Optional[str]:
    """Главная функция для извлечения условий доставки"""
    logger.info("Начало извлечения условий доставки")

    if await is_paste_format(page):
        return await parse_delivery_conditions_paste(page)
    else:
        return await parse_delivery_conditions_html(page)


async def parse_delivery_conditions_paste(page: Page) -> Optional[str]:
    """Извлечение условий доставки для формата paste"""
    logger.debug("Используется парсер для формата paste")

    conditions = []
    await expand_collapse_blocks(page)

    try:
        sections = await page.query_selector_all("div.collapse__content section.blockInfo__section")

        # 1. Проверяем информацию о сроке исполнения
        for section in sections:
            try:
                info_spans = await section.query_selector_all("span.section__info")
                for info in info_spans:
                    text = await info.text_content()
                    if "включает в том числе приемку" in text:
                        conditions.append("Срок исполнения включает приемку и оплату товара")
                        break
            except:
                continue

        # 2. Односторонний отказ
        for section in sections:
            try:
                title = await section.query_selector("span.section__title")
                if title:
                    title_text = await title.text_content()
                    if "односторонн" in title_text.lower() and "отказ" in title_text.lower():
                        info = await section.query_selector("span.section__info")
                        if info:
                            info_text = await info.text_content()
                            if "да" in info_text.lower():
                                conditions.append(
                                    "Предусмотрена возможность одностороннего отказа от исполнения контракта")
                                break
            except:
                continue

        # 3. Обеспечение исполнения контракта
        for i, section in enumerate(sections):
            try:
                title = await section.query_selector("span.section__title")
                if title:
                    title_text = await title.text_content()
                    if "Требуется обеспечение исполнения контракта" in title_text:
                        info = await section.query_selector("span.section__info")
                        if info:
                            info_text = await info.text_content()
                            if "да" in info_text.lower():
                                # Ищем размер обеспечения
                                for j in range(i + 1, min(i + 3, len(sections))):
                                    try:
                                        next_title = await sections[j].query_selector("span.section__title")
                                        if next_title:
                                            next_title_text = await next_title.text_content()
                                            if "Размер обеспечения исполнения контракта" in next_title_text:
                                                size_info = await sections[j].query_selector("span.section__info")
                                                if size_info:
                                                    size_text = await size_info.text_content()
                                                    percent_match = re.search(r'(\d+(?:[,.]\d+)?)\s*%', size_text)
                                                    if percent_match:
                                                        conditions.append(
                                                            f"Требуется обеспечение исполнения контракта: {percent_match.group(1)} %")
                                                    else:
                                                        conditions.append("Требуется обеспечение исполнения контракта")
                                                    break
                                    except:
                                        continue
                                break
            except:
                continue

        if conditions:
            result = "; ".join(conditions)
            logger.info(f"Найдены условия доставки: {len(conditions)} условий")
            return result

    except Exception as e:
        logger.error(f"Ошибка при парсинге условий (paste): {e}")

    return None


async def parse_delivery_conditions_html(page: Page) -> Optional[str]:
    """Извлечение условий доставки для формата html_content"""
    logger.debug("Используется парсер для формата html_content")

    conditions = []

    try:
        sections = await page.query_selector_all("section.blockInfo__section")

        # 1. Проверяем информацию о сроке исполнения
        for section in sections:
            try:
                info_spans = await section.query_selector_all("span.section__info")
                for info in info_spans:
                    text = await info.text_content()
                    if "включает в том числе приемку" in text:
                        conditions.append("Срок исполнения включает приемку и оплату товара")
                        break
            except:
                continue

        # 2. Односторонний отказ
        for section in sections:
            try:
                title = await section.query_selector("span.section__title")
                if title:
                    title_text = await title.text_content()
                    if "односторонн" in title_text.lower() and "отказ" in title_text.lower():
                        info = await section.query_selector("span.section__info")
                        if info:
                            info_text = await info.text_content()
                            if "да" in info_text.lower():
                                conditions.append(
                                    "Предусмотрена возможность одностороннего отказа от исполнения контракта")
            except:
                continue

        # 3. Обеспечение исполнения контракта
        all_sections = await page.query_selector_all("section.blockInfo__section")
        for i, section in enumerate(all_sections):
            try:
                title = await section.query_selector("span.section__title")
                if title:
                    title_text = await title.text_content()
                    if "Требуется обеспечение исполнения контракта" in title_text:
                        info = await section.query_selector("span.section__info")
                        if info:
                            info_text = await info.text_content()
                            if "да" in info_text.lower():
                                # Ищем размер
                                for j in range(i + 1, min(i + 3, len(all_sections))):
                                    try:
                                        next_title = await all_sections[j].query_selector("span.section__title")
                                        if next_title:
                                            next_title_text = await next_title.text_content()
                                            if "Размер обеспечения исполнения контракта" in next_title_text:
                                                size_info = await all_sections[j].query_selector("span.section__info")
                                                if size_info:
                                                    size_text = await size_info.text_content()
                                                    percent_match = re.search(r'(\d+(?:[,.]\d+)?)\s*%', size_text)
                                                    if percent_match:
                                                        conditions.append(
                                                            f"Требуется обеспечение исполнения контракта: {percent_match.group(1)} %")
                                                    else:
                                                        conditions.append("Требуется обеспечение исполнения контракта")
                                                    break
                                    except:
                                        continue
            except:
                continue

        if conditions:
            result = "; ".join(conditions)
            logger.info(f"Найдены условия доставки: {len(conditions)} условий")
            return result

    except Exception as e:
        logger.error(f"Ошибка при парсинге условий (html): {e}")

    return None