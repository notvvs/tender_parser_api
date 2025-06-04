from fastapi import APIRouter
from typing import Dict


router = APIRouter()


@router.get("/ping")
async def ping() -> Dict[str, str]:
    """Простая проверка доступности"""
    return {"status": "pong"}


