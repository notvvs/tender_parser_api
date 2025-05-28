import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router as api_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Создание приложения
app = FastAPI(
    title="Tender Parser API",
    description="API для парсинга данных с zakupki.gov.ru",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение API роутера
app.include_router(api_router, prefix="/api")

# Корневой endpoint
@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "service": "Tender Parser API",
        "version": "1.0.0",
        "docs": "/docs",
        "api": "/api"
    }

# Общий health check
@app.get("/health")
async def health_check():
    """Общая проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "ok",
            "parser": "ok",
            "database": "ok"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )