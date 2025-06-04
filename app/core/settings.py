from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения"""

    # Playwright
    browser_headless: bool = True
    browser_timeout: int = 30000

    # Ключ доступа
    api_key: str = "api_key"

    class Config:
        env_file = ".env"


# Создаем экземпляр настроек
settings = Settings()
