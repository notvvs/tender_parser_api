from app.parsers.tender_feature_parsers.documents_info import get_tender_documents
from app.parsers.tender_feature_parsers.tender_info import get_tender_info
from app.parsers.tender_feature_parsers.items_info import get_tender_items
from app.schemas.tender import TenderData
from app.utils.create_driver import create_driver


def get_tender(url: str) -> TenderData:
    """Функция для получения всей информации о тендере"""
    driver = create_driver()

    try:
        driver.get(url)

        tenderInfo = get_tender_info(driver)
        items = get_tender_items(driver)
        generalRequirements = None
        attachments = get_tender_documents(url)

        return TenderData(tenderInfo=tenderInfo,
                          items=items,
                          generalRequirements=generalRequirements,
                          attachments=attachments)

    finally:
        driver.quit()
