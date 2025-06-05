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

    return tender
