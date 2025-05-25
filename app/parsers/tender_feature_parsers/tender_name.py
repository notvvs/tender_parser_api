from selenium.webdriver.common.by import By

def get_tender_name(driver) -> str:
    """Извлечение наименования закупки"""
    try:
        return driver.find_element(
            By.XPATH,
            "//section[.//span[text()='Наименование объекта закупки']]/span[@class='section__info']"
        ).text
    except:
        return ""