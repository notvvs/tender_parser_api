from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.attachments import Attachment
from app.models.general import TenderInfo
from app.models.items import Item
from app.models.tender_requirements import GeneralRequirements


class TenderData(BaseModel):
    """Полные данные о тендере"""
    tenderInfo: TenderInfo = Field(..., description="Основная информация")
    items: List[Item] = Field(default_factory=list, description="Позиции закупки")
    generalRequirements: Optional[GeneralRequirements] = Field(
        default_factory=GeneralRequirements,
        description="Общие требования"
    )
    attachments: List[Attachment] = Field(default_factory=list, description="Документы")