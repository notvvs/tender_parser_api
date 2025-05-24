from typing import Optional
from pydantic import BaseModel, Field

class Attachment(BaseModel):
    """Прикрепленный документ"""
    name: str = Field(..., description="Название документа")
    type: str = Field(default="document", description="Тип документа")
    description: Optional[str] = Field(None, description="Описание")
    url: str = Field(..., description="Ссылка на документ")