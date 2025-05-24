from typing import Optional
from pydantic import BaseModel, Field
from app.models.items import Price


class DeliveryInfo(BaseModel):
    """Информация о доставке"""
    deliveryAddress: Optional[str] = Field(None, description="Адрес доставки")
    deliveryTerm: Optional[str] = Field(None, description="Срок доставки")
    deliveryConditions: Optional[str] = Field(None, description="Условия доставки")


class PaymentInfo(BaseModel):
    """Информация об оплате"""
    paymentTerm: Optional[str] = Field(None, description="Срок оплаты")
    paymentMethod: Optional[str] = Field(None, description="Способ оплаты")
    paymentConditions: Optional[str] = Field(None, description="Реквизиты")


class TenderInfo(BaseModel):
    """Основная информация о тендере"""
    tenderName: str = Field(..., description="Наименование закупки")
    tenderNumber: str = Field(..., description="Номер закупки")
    customerName: str = Field(..., description="Наименование заказчика")
    description: Optional[str] = Field(None, description="Описание закупки")
    purchaseType: str = Field(default="Электронный аукцион", description="Способ определения поставщика")
    financingSource: Optional[str] = Field(None, description="Источник финансирования")
    maxPrice: Optional[Price] = Field(None, description="Начальная (максимальная) цена")
    deliveryInfo: Optional[DeliveryInfo] = Field(default_factory=DeliveryInfo, description="Информация о доставке")
    paymentInfo: Optional[PaymentInfo] = Field(default_factory=PaymentInfo, description="Информация об оплате")


