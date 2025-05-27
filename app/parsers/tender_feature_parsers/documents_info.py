import re
import logging
from typing import List

from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.schemas.attachments import Attachment
from app.utils.create_driver import get_driver
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


def get_tender_documents(tender_url: str) -> List[Attachment]:
    """Основная функция для парсинга документов тендера"""
    documents = []
    documents_url = get_documents_url(tender_url)

    logger.info(f"Начало парсинга документов для тендера: {tender_url}")

    try:
        with get_driver() as driver:
            # Загружаем страницу с документами
            driver.get(documents_url)
            logger.debug("Страница документов загружена")

            # Ждем загрузки блока с документами
            wait = WebDriverWait(driver, 10)
            try:
                block = wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "blockFilesTabDocs"))
                )
                logger.debug("Блок с документами найден")
            except TimeoutException:
                logger.warning("Блок с документами не найден. Возможно, документов нет.")
                return documents

            # Раскрываем скрытые документы
            expand_all_documents(driver)

            # Находим все строки с документами
            doc_rows = block.find_elements(By.CSS_SELECTOR, ".attachment.row")
            logger.info(f"Найдено строк с документами: {len(doc_rows)}")

            for idx, row in enumerate(doc_rows):
                try:
                    # Ищем ссылку на документ
                    link = row.find_element(By.CSS_SELECTOR, "a[href*='filestore']")
                    url = link.get_attribute('href')

                    if not url:
                        logger.warning(f"Пустой URL для документа #{idx + 1}")
                        continue

                    # Получаем название
                    name = link.text.strip()
                    if not name:
                        # Если текст пустой, берем из title без расширения
                        title = link.get_attribute('title')
                        if title:
                            name = re.sub(r'\.\w+$', '', title)
                        else:
                            name = f"Документ #{idx + 1}"
                            logger.warning(f"Не удалось получить название для документа #{idx + 1}")

                    # Определяем тип файла
                    file_type = 'document'
                    try:
                        icon = row.find_element(By.CSS_SELECTOR, "img[src*='/icons/type/']")
                        icon_src = icon.get_attribute('src')
                        file_type = get_file_type(icon_src)
                        logger.debug(f"Определен тип файла: {file_type} для {name}")
                    except NoSuchElementException:
                        logger.debug(f"Не найдена иконка типа для документа: {name}")

                    # Создаем документ
                    doc = Attachment(
                        name=name,
                        type=file_type,
                        url=url,
                        description=None
                    )
                    documents.append(doc)
                    logger.debug(f"Документ #{idx + 1} успешно обработан: {name}")

                except NoSuchElementException as e:
                    logger.warning(f"Не найдены обязательные элементы для документа #{idx + 1}: {e}")
                except Exception as e:
                    logger.error(f"Ошибка при парсинге документа #{idx + 1}: {e}")

    except Exception as e:
        logger.error(f'Критическая ошибка при парсинге документов: {e}', exc_info=True)

    logger.info(f"Парсинг документов завершен. Найдено документов: {len(documents)}")
    return documents