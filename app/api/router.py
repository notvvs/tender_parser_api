from fastapi import APIRouter

from app.api.v1 import router as v1_router

router = APIRouter()

# Подключаем версии API
router.include_router(v1_router.api_router, prefix="/v1")
