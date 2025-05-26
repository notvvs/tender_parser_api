
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager

def create_driver(headless=True) -> WebDriver:
    """Создает Chrome драйвер с настройками для стабильной работы"""
    options = Options()

    # Режим работы
    if headless:
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')

    # Стабильность
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-features=VizDisplayCompositor')

    # Производительность
    options.add_argument('--disable-images')
    options.add_argument('--disable-plugins')
    options.add_argument('--disable-extensions')

    # Размер окна
    options.add_argument('--window-size=1920,1080')

    # Обход защиты от ботов
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # User-Agent
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    # Отключение уведомлений
    prefs = {'profile.default_content_setting_values.notifications': 2}
    options.add_experimental_option('prefs', prefs)

    # Игнорирование SSL ошибок
    options.add_argument('--ignore-certificate-errors')

    # Память
    options.add_argument('--memory-pressure-off')

    return webdriver.Chrome(service=Service(executable_path='C:/Users/ruzik/PycharmProjects/work/parser_service/chromedriver.exe'), options=options)