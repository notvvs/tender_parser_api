from fastapi import HTTPException, Header, status

from app.core.settings import settings


def verify_api_key(x_api_key: str = Header(None)):
    """Проверяет API ключ в заголовке запроса"""
    # Если авторизация отключена, пропускаем проверку
    if not settings.enable_auth:
        return "auth_disabled"

    # Проверяем наличие ключа
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API ключ не предоставлен",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    # Проверяем правильность ключа
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неверный API ключ"
        )

    return x_api_key