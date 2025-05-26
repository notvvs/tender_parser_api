import re
from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.schemas.attachments import Attachment
from app.utils.create_driver import create_driver
from app.utils.expand_elements import expand_all_documents
from app.utils.format_check import get_file_type


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
    driver = create_driver()
    documents = []

    try:
        # Получаем URL страницы с документами
        documents_url = get_documents_url(tender_url)

        # Загружаем страницу
        driver.get(documents_url)

        # Ждем загрузки блока с документами
        wait = WebDriverWait(driver, 10)
        block = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "blockFilesTabDocs"))
        )
        # Раскрываем скрытые документы
        expand_all_documents(driver)

        # Находим все строки с документами
        doc_rows = block.find_elements(By.CSS_SELECTOR, ".attachment.row")

        for row in doc_rows:
            try:
                # Ищем ссылку на документ
                link = row.find_element(By.CSS_SELECTOR, "a[href*='filestore']")
                url = link.get_attribute('href')

                # Получаем название
                name = link.text.strip()
                if not name:
                    # Если текст пустой, берем из title без расширения
                    title = link.get_attribute('title')
                    if title:
                        name = re.sub(r'\.\w+$', '', title)

                # Определяем тип файла
                file_type = 'document'
                try:
                    icon = row.find_element(By.CSS_SELECTOR, "img[src*='/icons/type/']")
                    icon_src = icon.get_attribute('src')
                    file_type = get_file_type(icon_src)
                except:
                    pass

                # Создаем документ
                doc = Attachment(
                    name=name,
                    type=file_type,
                    url=url,
                    description=None
                )
                documents.append(doc)

            except Exception as e:
                print(f"Ошибка при парсинге документа: {e}")
                continue

    finally:
        driver.quit()

    return documents
