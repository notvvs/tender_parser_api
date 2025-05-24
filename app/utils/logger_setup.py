import logging
import os
from datetime import datetime


def setup_logging():
    """
    Настраивает логирование для приложения
    """
    # Создаем директорию для логов, если она не существует
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Текущая дата для имени файла
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_file = f"{log_dir}/scraper_{current_date}.log"

    # Конфигурация логгера
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )

    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info(f"Логирование настроено. Лог-файл: {log_file}")

    return logger
