# src/api/auth.py
import uuid

from fastapi import APIRouter, Request, Security, Body
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

# src/api/auth.py
from src.api.dependencies import DBDep, UserIdDep, get_current_user, get_current_user_id
from src.config import settings
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

# src/api/auth.py
from fastapi import APIRouter, Request, Security, Body, Response   # + Response

class RefreshIn(BaseModel):
    refresh_token: str | None = None

@router.post("/logout")
async def logout_user(db: DBDep, request: Request, body: RefreshIn | None = Body(default=None)):
    token = request.cookies.get("refresh_token")
    if not token:
        auth = request.headers.get("Authorization")
        if auth and auth.startswith("Bearer "):
            token = auth[len("Bearer "):].strip()
    if not token and body and body.refresh_token:
        token = body.refresh_token
    if not token:
        raise to_http(AuthorizationException("Требуется refresh токен"))
    try:
        await AuthServices(db).logout_current(token)
        return {"detail": "Выход из системы"}
    except AppException as e:
        raise to_http(e)
    except Exception:
        # например, DecodeError «Not enough segments»
        raise to_http(AuthenticationException("Invalid refresh token"))




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
async def refresh_tokens(db: DBDep, request: Request, body: RefreshIn | None = Body(default=None)):
    token = request.cookies.get("refresh_token")
    if not token:
        auth = request.headers.get("Authorization")
        if auth and auth.startswith("Bearer "):
            token = auth[len("Bearer "):].strip()
    if not token and body and body.refresh_token:
        token = body.refresh_token

    if not token:
        raise to_http(AuthorizationException("Требуется refresh токен"))
    try:
        return await AuthServices(db).refresh(token)
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
async def login_user(db: DBDep, data: LoginIn, request: Request, response: Response):
    try:
        ua = request.headers.get("user-agent")
        ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or (
            request.client.host if request.client else None
        )
        pair = await AuthServices(db).login(data, user_agent=ua, ip=ip)

        # refresh в httpOnly cookie
        response.set_cookie(
            "refresh_token",
            pair.refresh_token,
            httponly=True,
            secure=not settings.DEBUG,  # DEV: False, PROD: True
            samesite="lax",             # DEV: lax (иначе None требует secure)
            path="/",
            max_age=settings.REFRESH_EXPIRES,
        )
        return pair
    except AppException as e:
        raise to_http(e)
