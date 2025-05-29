from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения"""

    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "tenders_db"

    # Playwright
    browser_headless: bool = True
    browser_timeout: int = 30000

    # Ключ доступа
    api_key: str = None

    # Парсер
    max_concurrent_tasks: int = 10
    parser_max_retries: int = 3

    # Очистка задач
    task_cleanup_hours: int = 24

    class Config:
        env_file = ".env"


# Создаем экземпляр настроек
settings = Settings()