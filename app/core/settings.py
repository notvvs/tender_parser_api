import os
from pathlib import Path

from dotenv import load_dotenv

# Загружаем .env файл
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


class Settings:
    """Настройки приложения"""

    # MongoDB
    mongodb_url: str = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    mongodb_db_name: str = os.getenv("MONGODB_DB_NAME", "tenders_db")

    # Playwright
    browser_headless: bool = os.getenv("BROWSER_HEADLESS", True)
    browser_timeout: int = 30000

    # Парсер
    max_concurrent_tasks: int = os.getenv("MAX_CONCURRENT_TASKS", 10)

    # Очистка задач
    task_cleanup_hours: int = 24

    # Безопасность
    api_key: str = os.getenv("API_KEY", "def_api_key")



# Создаем экземпляр настроек
settings = Settings()
