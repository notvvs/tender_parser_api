import logging
from fastapi import FastAPI

from app.api.router import router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


# Создание приложения
app = FastAPI(
    title="Tender Parser Microservice",
    description="Микросервис для асинхронного парсинга тендеров с zakupki.gov.ru",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.include_router(router, prefix="/api")