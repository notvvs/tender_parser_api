import logging

from fastapi import FastAPI

from app.parsers.all_tender_info import get_tender

from app.repository.database import repository
from app.schemas.tender import TenderData

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


logger = logging.getLogger(__name__)

app = FastAPI(
    title="Parser API",
    description="API для парсинга данных с zakupki.gov.ru",
    version="1.0.0"
)


@app.post('/')
async def test(url) -> TenderData:
    data = get_tender(url)
    await repository.save(data.model_dump())
    return data