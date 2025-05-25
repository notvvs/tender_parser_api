from app.parsers.tender_feature_parsers.delivery_address import get_delivery_address
from app.parsers.tender_feature_parsers.delivery_conditions import get_delivery_conditions
from app.parsers.tender_feature_parsers.delivery_term import get_delivery_term
from app.schemas.general import DeliveryInfo


def get_delivery_info(driver) -> DeliveryInfo:

    deliveryAddress = get_delivery_address(driver)
    deliveryTerm = get_delivery_term(driver)
    deliveryConditions = get_delivery_conditions(driver)

    return DeliveryInfo(deliveryAddress=deliveryAddress,
                        deliveryTerm=deliveryTerm,
                        deliveryConditions=deliveryConditions)