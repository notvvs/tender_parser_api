from typing import Optional, List
from pydantic import BaseModel, Field

from app.schemas.attachments import Attachment
from app.schemas.general import TenderInfo
from app.schemas.items import Item
from app.schemas.tender_requirements import GeneralRequirements


class TenderData(BaseModel):
    """Полные данные о тендере"""
    tenderInfo: TenderInfo = Field(..., description="Основная информация")
    items: Optional[List[Item]] = Field(default_factory=list, description="Позиции закупки")
    generalRequirements: Optional[GeneralRequirements] = Field(
        default_factory=GeneralRequirements,
        description="Общие требования"
    )
    attachments: List[Attachment] = Field(default_factory=list, description="Документы")