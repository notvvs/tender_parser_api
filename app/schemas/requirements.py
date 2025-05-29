from typing import Optional

from pydantic import BaseModel, Field


class GeneralRequirements(BaseModel):
    """Общие требования к закупке"""

    qualityRequirements: Optional[str] = Field(
        None, description="Требования к качеству"
    )
    packagingRequirements: Optional[str] = Field(
        None, description="Требования к упаковке"
    )
    markingRequirements: Optional[str] = Field(
        None, description="Требования к маркировке"
    )
    warrantyRequirements: Optional[str] = Field(
        None, description="Гарантийные требования"
    )
    safetyRequirements: Optional[str] = Field(
        None, description="Требования безопасности"
    )
    regulatoryRequirements: Optional[str] = Field(
        None, description="Нормативные требования"
    )
