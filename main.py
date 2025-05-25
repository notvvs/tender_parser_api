import logging

from fastapi import FastAPI

from app.parsers.tender_info import get_tender_info
from app.schemas.general import TenderInfo
from app.utils.create_driver import create_driver

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


logger = logging.getLogger(__name__)

app = FastAPI(
    title="Zakupki.gov.ru Parser API",
    description="API для парсинга данных с zakupki.gov.ru",
    version="1.0.0"
)


@app.post('/')
async def test(url) -> TenderInfo:
    driver = create_driver()
    driver.get(url)
    return get_tender_info(driver)