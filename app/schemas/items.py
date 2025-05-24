from typing import Optional, List
from pydantic import BaseModel, Field

class Price(BaseModel):
    """Модель для цены"""
    amount: float = Field(description="Сумма")
    currency: str = Field(default="RUB", description="Валюта")


class ItemCharacteristic(BaseModel):
    """Характеристика товара"""
    id: int = Field(..., description="ID характеристики")
    name: str = Field(..., description="Наименование характеристики")
    value: str = Field(..., description="Значение характеристики")
    unit: Optional[str] = Field(None, description="Единица измерения")
    type: str = Field(default="Качественная", description="Тип характеристики")
    required: bool = Field(default=True, description="Обязательная характеристика")
    changeable: bool = Field(default=False, description="Может изменяться участником")
    fillInstruction: Optional[str] = Field(None, description="Инструкция по заполнению")


class Item(BaseModel):
    """Позиция закупки"""
    id: int = Field(..., description="ID позиции")
    name: str = Field(..., description="Наименование товара/услуги")
    okpd2Code: Optional[str] = Field(None, description="Код ОКПД2")
    ktruCode: Optional[str] = Field(None, description="Код КТРУ")
    quantity: int = Field(..., description="Количество")
    unitOfMeasurement: str = Field(..., description="Единица измерения")
    unitPrice: Optional[Price] = Field(None, description="Цена за единицу")
    totalPrice: Optional[Price] = Field(None, description="Общая стоимость")
    characteristics: List[ItemCharacteristic] = Field(default_factory=list, description="Характеристики")
    additionalRequirements: Optional[str] = Field(None, description="Дополнительные требования")