from app.parsers.tender_feature_parsers.payment_features.payment_conditions import get_payment_conditions
from app.parsers.tender_feature_parsers.payment_features.payment_method import get_payment_method
from app.parsers.tender_feature_parsers.payment_features.payment_term import get_payment_term
from app.schemas.general import PaymentInfo


def get_payment_info(driver):

    paymentTerm = get_payment_term(driver)
    paymentMethod = get_payment_method(driver)
    paymentConditions = get_payment_conditions(driver)

    return PaymentInfo(paymentTerm=paymentTerm,
                       paymentMethod=paymentMethod,
                       paymentConditions=paymentConditions)