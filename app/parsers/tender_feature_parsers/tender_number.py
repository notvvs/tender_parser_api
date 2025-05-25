from selenium.webdriver.common.by import By


def get_tender_number(driver) -> str:
    """Извлечение номера закупки"""
    try:
        text = driver.find_element(
            By.XPATH,
            "//span[@class='cardMainInfo__purchaseLink distancedText']/a"
        ).text
        if '№' in text:
            return text.split('№')[-1].strip()
        return text
    except:
        return ''