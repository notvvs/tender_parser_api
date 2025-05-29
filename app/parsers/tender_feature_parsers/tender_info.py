from playwright.async_api import Page

from app.parsers.tender_feature_parsers.delivery_info import get_delivery_info
from app.parsers.tender_feature_parsers.payment_info import get_payment_info
from app.parsers.tender_feature_parsers.tender_features.customer_name import (
    get_customer_name,
)
from app.parsers.tender_feature_parsers.tender_features.financing_source import (
    get_financing_source,
)
from app.parsers.tender_feature_parsers.tender_features.max_price import get_price_info
from app.parsers.tender_feature_parsers.tender_features.purchase_type import (
    get_purchase_type,
)
from app.parsers.tender_feature_parsers.tender_features.tender_name import (
    get_tender_name,
)
from app.parsers.tender_feature_parsers.tender_features.tender_number import (
    get_tender_number,
)
from app.schemas.general import TenderInfo


async def get_tender_info(page: Page):
    """Основная функция для получения информации о тендере"""
    tenderName = await get_tender_name(page)
    tenderNumber = await get_tender_number(page)
    customerName = await get_customer_name(page)
    purchaseType = await get_purchase_type(page)
    financingSource = await get_financing_source(page)
    maxPrice = await get_price_info(page)
    deliveryInfo = await get_delivery_info(page)
    paymentInfo = await get_payment_info(page)

    return TenderInfo(
        tenderName=tenderName,
        tenderNumber=tenderNumber,
        customerName=customerName,
        purchaseType=purchaseType,
        maxPrice=maxPrice,
        deliveryInfo=deliveryInfo,
        financingSource=financingSource,
        paymentInfo=paymentInfo,
    )
