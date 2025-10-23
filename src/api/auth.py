# src/api/auth.py
import uuid

from fastapi import APIRouter, Request, Security, Body
from sqlalchemy.exc import IntegrityError

# src/api/auth.py
from src.api.dependencies import DBDep, UserIdDep, get_current_user, get_current_user_id
from src.core.security import decode_jwt
from src.exceptions import to_http, AlreadyExistsException, AppException, AuthorizationException, \
    AuthenticationException
from src.models.users import UsersOrm
from src.schemas.users import UserAdd, User, LoginIn, TokenPair
from src.services.auth import AuthServices

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/me", response_model=User)
async def me(db: DBDep, user: UsersOrm = Security(get_current_user)):
    # дальше твоя логика 1:1
    if not user:
        raise to_http(AuthorizationException("Пользователь не найден"))
    return User.model_validate(user)

@router.post("/logout")
async def logout_user(
    db: DBDep,
    request: Request,
    token_body: dict | None = Body(default=None)
):
    """Выход из текущей сессии"""
    # 1️⃣ Ищем refresh-токен
    token = request.cookies.get("refresh_token")
    if not token:
        auth = request.headers.get("Authorization")
        if auth and auth.startswith("Bearer "):
            token = auth[len("Bearer "):].strip()
    if not token and token_body and "refresh_token" in token_body:
        token = token_body["refresh_token"]

    if not token:
        raise to_http(AuthorizationException("Требуется refresh токен"))

    # 2️⃣ Вызываем сервис
    try:
        service = AuthServices(db)
        await service.logout_current(token)
        return {"detail": "Выход из системы"}
    except AppException as e:
        raise to_http(e)



@router.post("/logout_all")
async def logout_all(
    db: DBDep,
    user_id: int = Security(get_current_user_id),
):
    """Завершить все сессии пользователя (выйти со всех устройств)."""
    try:
        await AuthServices(db).logout_all(user_id)
        return {"detail": "Все сессии завершены"}
    except AppException as e:
        raise to_http(e)


@router.post("/refresh", response_model=TokenPair)
async def refresh_tokens(db: DBDep, token_pair: TokenPair):
    try:
        return await AuthServices(db).refresh(token_pair.refresh_token)
    except AppException as e:
        raise to_http(e)


@router.post("/register", status_code=201, response_model=User)
async def register_user(db: DBDep, data: UserAdd):
    try:
        return await AuthServices(db).register(data)
    except IntegrityError:
        raise to_http(AlreadyExistsException("Пользователь с таким email уже существует"))
    except AppException as e:
        raise to_http(e)


@router.post("/login", response_model=TokenPair)
async def login_user(db: DBDep, data: LoginIn, request: Request):
    try:
        ua = request.headers.get("user-agent")
        ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or (
            request.client.host if request.client else None
        )
        return await AuthServices(db).login(data, user_agent=ua, ip=ip)
    except AppException as e:
        raise to_http(e)
