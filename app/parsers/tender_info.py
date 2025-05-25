from app.parsers.delivery_info import get_delivery_info
from app.parsers.payment_info import get_payment_info
from app.parsers.tender_feature_parsers.tender_features.customer_name import get_customer_name
from app.parsers.tender_feature_parsers.tender_features.financing_source import get_financing_source
from app.parsers.tender_feature_parsers.tender_features.max_price import get_price_info
from app.parsers.tender_feature_parsers.tender_features.purchase_type import get_purchase_type
from app.parsers.tender_feature_parsers.tender_features.tender_name import get_tender_name
from app.parsers.tender_feature_parsers.tender_features.tender_number import get_tender_number
from app.schemas.general import TenderInfo
from app.utils.create_driver import create_driver


def get_tender_info(driver):

    tenderName = get_tender_name(driver)
    tenderNumber = get_tender_number(driver)
    customerName = get_customer_name(driver)
    purchaseType = get_purchase_type(driver)
    financingSource = get_financing_source(driver)
    maxPrice = get_price_info(driver)
    deliveryInfo = get_delivery_info(driver)
    paymentInfo = get_payment_info(driver)

    return TenderInfo(tenderName=tenderName,
                      tenderNumber=tenderNumber,
                      customerName=customerName,
                      purchaseType=purchaseType,
                      maxPrice=maxPrice,
                      deliveryInfo=deliveryInfo,
                      financingSource=financingSource,
                      paymentInfo=paymentInfo
                      ).model_dump_json()

driver = create_driver()
driver.get('https://zakupki.gov.ru/epz/order/notice/ea20/view/common-info.html?regNumber=0372200001725000078')
print(get_tender_info(driver))