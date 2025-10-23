# src/api/dependencies.py
from typing import Annotated
from fastapi import Depends, Request, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.config import settings
from src.core.security import decode_jwt
from src.exceptions import AuthorizationException, ObjectNotFoundException
from src.utils.db_manager import DBManager
from src.database import async_session_maker
from src.connectors.redis_connector import RedisManager
from src.models.users import UsersOrm


# ---------- DB ----------
def db_manager():
    return DBManager(session_factory=async_session_maker)


async def get_db():
    async with db_manager() as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]


# ---------- AUTH ----------
# Это триггер для Swagger, чтобы показать кнопку Authorize
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    db: DBDep,
    creds: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> UsersOrm:
    """Извлекает пользователя из access токена"""
    token = None

    # 1️⃣ сначала пробуем заголовок Authorization: Bearer <token>
    if creds and creds.scheme.lower() == "bearer":
        token = creds.credentials

    # 2️⃣ если нет — пробуем cookie (на случай SSR)
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise AuthorizationException("Missing access token")

    # 3️⃣ декодируем JWT и валидируем тип
    payload = decode_jwt(
        token,
        secret_key=settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    if payload.get("type") != "access":
        raise AuthorizationException("Access token required")

    # 4️⃣ достаём юзера
    user = await db.users.get_by_id(int(payload["sub"]))
    if not user:
        raise ObjectNotFoundException("User not found")

    return user


async def get_current_user_id(
    user: Annotated[UsersOrm, Depends(get_current_user)]
) -> int:
    """Возвращает только id пользователя"""
    return int(user.id)


UserIdDep = Annotated[int, Depends(get_current_user_id)]


# ---------- REDIS ----------
def get_redis(request: Request) -> RedisManager:
    rm: RedisManager = request.app.state.redis_manager
    if not rm or not rm.redis:
        raise RuntimeError("Redis is not connected")
    return rm


RedisDep = Annotated[RedisManager, Depends(get_redis)]
