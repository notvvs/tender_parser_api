import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from app.api import router as api_router
from app.services.task_manager import get_task_manager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Инициализация при старте
    logger.info("Запуск микросервиса парсера")

    # Инициализируем менеджер задач
    task_manager = get_task_manager()
    await task_manager.initialize()

    # Запускаем периодическую очистку
    async def periodic_cleanup():
        while True:
            await asyncio.sleep(3600)  # Каждый час
            try:
                await task_manager.cleanup_old_tasks(24)
                # Логируем статистику
                stats = await task_manager.get_stats()
                logger.info(f"Статистика задач: {stats}")
            except Exception as e:
                logger.error(f"Ошибка при очистке задач: {e}")

    cleanup_task = asyncio.create_task(periodic_cleanup())

    logger.info("Микросервис успешно запущен")

    yield

    # Очистка при остановке
    logger.info("Остановка микросервиса")
    cleanup_task.cancel()

    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


# Создание приложения
app = FastAPI(
    title="Tender Parser Microservice",
    description="Микросервис для асинхронного парсинга тендеров с zakupki.gov.ru",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
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
                "endpoints": {
                    "health": "/api/v1/health",
                    "parser": "/api/v1/parser"
                }
            }
        }
    }


@app.get("/api", tags=["root"])
async def api_info():
    """Информация об API"""
    return {
        "versions": ["v1"],
        "current": "v1",
        "endpoints": {
            "v1": {
                "health": "/api/v1/health",
                "ping": "/api/v1/ping",
                "parse": "/api/v1/parser/parse",
                "task_status": "/api/v1/parser/task/{task_id}/status",
                "task_result": "/api/v1/parser/task/{task_id}/result",
                "task_tender": "/api/v1/parser/task/{task_id}/tender"
            }
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )