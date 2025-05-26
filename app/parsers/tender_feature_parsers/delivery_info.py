from selenium.webdriver.chrome.webdriver import WebDriver
from app.parsers.tender_feature_parsers.delivery_features.address import get_delivery_address
from app.parsers.tender_feature_parsers.delivery_features.conditions import get_delivery_conditions
from app.parsers.tender_feature_parsers.delivery_features.term import get_delivery_term
from app.schemas.general import DeliveryInfo


def get_delivery_info(driver: WebDriver) -> DeliveryInfo:
    """Основная функция для получения всей информации о доставке"""
    deliveryAddress = get_delivery_address(driver)
    deliveryTerm = get_delivery_term(driver)
    deliveryConditions = get_delivery_conditions(driver)

    return DeliveryInfo(deliveryAddress=deliveryAddress,
                        deliveryTerm=deliveryTerm,
                        deliveryConditions=deliveryConditions)