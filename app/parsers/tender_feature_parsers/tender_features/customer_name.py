from selenium.webdriver.common.by import By


def get_customer_name(driver) -> str:
    """Извлечение наименования заказчика"""
    try:
        return driver.find_element(
            By.XPATH,
            "//section[.//span[text()='Организация, осуществляющая размещение']]/span[@class='section__info']"
        ).text
    except:
        return ""
