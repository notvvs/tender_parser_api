import logging

from playwright.async_api import Page

logger = logging.getLogger(__name__)


async def is_paste_format(page: Page) -> bool:
    """Проверка формата страницы - paste или html_content"""
    try:
        collapse_blocks = await page.query_selector_all(
            "div.blockInfo__collapse.collapseInfo"
        )
        is_paste = len(collapse_blocks) > 0
        logger.debug(
            f"Определен формат страницы: {'paste' if is_paste else 'html_content'}"
        )
        return is_paste
    except Exception as e:
        logger.error(f"Ошибка при определении формата страницы: {e}")
        return False


def get_file_type(icon_src: str) -> str:
    """Определяет тип файла по URL иконки"""
    if "docx" in icon_src:
        return "docx"
    elif "doc" in icon_src:
        return "doc"
    elif "xlsx" in icon_src:
        return "xlsx"
    elif "xls" in icon_src:
        return "xls"
    elif "pdf" in icon_src:
        return "pdf"
    elif "zip" in icon_src or "rar" in icon_src:
        return "archive"
    else:
        return "document"
