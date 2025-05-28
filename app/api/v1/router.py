from fastapi import APIRouter

from app.api.v1.endpoints import health, parser

api_router = APIRouter()

# Подключаем эндпоинты
api_router.include_router(health.router, tags=["health"])
api_router.include_router(parser.router, prefix="/parser", tags=["parser"])
