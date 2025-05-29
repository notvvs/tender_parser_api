from playwright.async_api import Page

from app.parsers.tender_feature_parsers.delivery_features.address import (
    get_delivery_address,
)
from app.parsers.tender_feature_parsers.delivery_features.conditions import (
    get_delivery_conditions,
)
from app.parsers.tender_feature_parsers.delivery_features.term import get_delivery_term
from app.schemas.general import DeliveryInfo


async def get_delivery_info(page: Page) -> DeliveryInfo:
    """Основная функция для получения информации о доставке"""
    deliveryAddress = await get_delivery_address(page)
    deliveryTerm = await get_delivery_term(page)
    deliveryConditions = await get_delivery_conditions(page)

    return DeliveryInfo(
        deliveryAddress=deliveryAddress,
        deliveryTerm=deliveryTerm,
        deliveryConditions=deliveryConditions,
    )
