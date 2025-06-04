import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from app.api import router as api_router


# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)



# Создание приложения
app = FastAPI(
    title="Tender Parser Microservice",
    description="Микросервис для асинхронного парсинга тендеров с zakupki.gov.ru",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение API роутера
app.include_router(api_router.router, prefix="/api")


@app.get("/", tags=["root"])
async def root():
    """Корневой эндпоинт с информацией о сервисе"""
    return {
        "service": "Tender Parser Microservice",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
        "api": {
            "v1": {
                "base": "/api/v1",
                "endpoints": {"health": "/api/v1/health", "parser": "/api/v1/parser"},
            }
        },
    }




if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
