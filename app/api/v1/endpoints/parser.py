from fastapi import APIRouter, HTTPException, Depends

from app.core.auth import verify_api_key
from app.schemas.tender import TenderData
from app.services.parser_service import parser

router = APIRouter()


@router.post('/parse', response_model=TenderData, dependencies=[Depends(verify_api_key)])
async def parse(url: str) -> TenderData:

    tender = await parser.start_parsing(url)

    if not tender:
        raise HTTPException(
            status_code=404, detail="Тендер нe обработан"
        )

    # Преобразуем ObjectId в строку для JSON сериализации
    if "_id" in tender:
        tender["_id"] = str(tender["_id"])

    return tender
