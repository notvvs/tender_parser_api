from fastapi import APIRouter

from app.api.v1.endpoints import parser

api_router = APIRouter()

# Подключаем эндпоинты
api_router.include_router(parser.router, prefix="/parser", tags=["parser"])
