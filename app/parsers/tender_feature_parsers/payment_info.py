from playwright.async_api import Page

from app.parsers.tender_feature_parsers.payment_features.conditions import (
    get_payment_conditions,
)
from app.parsers.tender_feature_parsers.payment_features.method import (
    get_payment_method,
)
from app.parsers.tender_feature_parsers.payment_features.term import get_payment_term
from app.schemas.general import PaymentInfo


async def get_payment_info(page: Page):
    """Основная функция для получения информации о платежах"""
    paymentTerm = await get_payment_term(page)
    paymentMethod = await get_payment_method(page)
    paymentConditions = await get_payment_conditions(page)

    return PaymentInfo(
        paymentTerm=paymentTerm,
        paymentMethod=paymentMethod,
        paymentConditions=paymentConditions,
    )
