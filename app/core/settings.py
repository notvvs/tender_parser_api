from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Настройки приложения"""

    # Playwright
    browser_headless: bool = True
    browser_timeout: int = 15000

    # Ключ доступа
    api_key: str = Field(...)

    class Config:
        env_file = ".env"


# Создаем экземпляр настроек
settings = Settings()
