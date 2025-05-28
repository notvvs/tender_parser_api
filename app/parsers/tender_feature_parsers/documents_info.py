import re
import logging
from typing import List


from app.schemas.attachments import Attachment
from app.utils.create_driver import get_page
from app.utils.expand_elements import expand_all_documents
from app.utils.format_check import get_file_type

logger = logging.getLogger(__name__)

def get_documents_url(tender_url: str) -> str:
    """Преобразует URL общей информации в URL документов"""
    # Извлекаем regNumber из URL
    match = re.search(r'regNumber=(\d+)', tender_url)
    if not match:
        raise ValueError(f"Не найден regNumber в URL: {tender_url}")

    reg_number = match.group(1)
    return f"https://zakupki.gov.ru/epz/order/notice/ea20/view/documents.html?regNumber={reg_number}"


async def get_tender_documents(tender_url: str) -> List[Attachment]:
    """Основная функция для парсинга документов"""
    documents = []
    documents_url = get_documents_url(tender_url)

    logger.info(f"Начало парсинга документов: {tender_url}")

    try:
        async with get_page() as page:
            await page.goto(documents_url)
            logger.debug("Страница документов загружена")

            # Ждем загрузки блока
            try:
                await page.wait_for_selector(".blockFilesTabDocs", timeout=10000)
                logger.debug("Блок с документами найден")
            except:
                logger.warning("Блок с документами не найден")
                return documents

            # Раскрываем скрытые документы
            await expand_all_documents(page)

            # Находим все строки
            doc_rows = await page.query_selector_all(".attachment.row")
            logger.info(f"Найдено строк с документами: {len(doc_rows)}")

            for idx, row in enumerate(doc_rows):
                try:
                    # Ищем ссылку
                    link = await row.query_selector("a[href*='filestore']")
                    if not link:
                        continue

                    url = await link.get_attribute('href')
                    if not url:
                        logger.warning(f"Пустой URL для документа #{idx + 1}")
                        continue

                    # Получаем название
                    name = await link.text_content()
                    if not name:
                        title = await link.get_attribute('title')
                        if title:
                            name = re.sub(r'\.\w+$', '', title)
                        else:
                            name = f"Документ #{idx + 1}"

                    # Определяем тип
                    file_type = 'document'
                    try:
                        icon = await row.query_selector("img[src*='/icons/type/']")
                        if icon:
                            icon_src = await icon.get_attribute('src')
                            file_type = get_file_type(icon_src)
                    except:
                        pass

                    doc = Attachment(
                        name=name.strip(),
                        type=file_type,
                        url=url,
                        description=None
                    )
                    documents.append(doc)
                    logger.debug(f"Документ #{idx + 1} обработан: {name}")

                except Exception as e:
                    logger.error(f"Ошибка при парсинге документа #{idx + 1}: {e}")

    except Exception as e:
        logger.error(f'Критическая ошибка при парсинге документов: {e}', exc_info=True)

    logger.info(f"Парсинг документов завершен. Найдено: {len(documents)}")
    return documents