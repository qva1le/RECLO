from fastapi import APIRouter, Request, Security, Body, Response
from pydantic import BaseModel

from src.api.dependencies import DBDep, get_current_user, get_current_user_id, RedisDep
from src.config import settings
from src.exceptions import to_http, AuthorizationException, \
    AuthenticationException
from src.models.users import UsersOrm
from src.schemas.enums import UserStatus
from src.schemas.users import UserAdd, User, LoginIn, TokenPair
from src.services.auth import AuthServices
from src.services.verify import VerifyService

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/me", response_model=User)
async def me(
        db: DBDep,
        user: UsersOrm = Security(get_current_user)
):
    if user.status != UserStatus.active:
        raise to_http(AuthenticationException("Пользователь не активен"))

    return User.model_validate(user)


class RefreshIn(BaseModel):
    refresh_token: str | None = None


def extract_refresh_token(
        request: Request,
        body: RefreshIn | None
) -> str:
    token = request.cookies.get("refresh_token")

    if not token:
        auth = request.headers.get("Authorization")
        if auth and auth.startswith("Bearer "):
            token = auth[len("Bearer "):].strip()

    if not token and body and body.refresh_token:
        token = body.refresh_token

    if not token:
        raise to_http(AuthorizationException("Требуется refresh токен"))

    return token


@router.post("/logout")
async def logout_user(
        db: DBDep,
        request: Request,
        response: Response,
        body: RefreshIn | None = Body(default=None),
):
    token = extract_refresh_token(request, body)

    await AuthServices(db).logout_current(token)

    response.delete_cookie("refresh_token", path="/")

    return {"detail": "Выход из системы"}


@router.post("/logout_all")
async def logout_all(
    db: DBDep,
    user_id: int = Security(get_current_user_id),
):
    await AuthServices(db).logout_all(user_id)
    return {"detail": "Все сессии завершены"}


@router.post("/refresh", response_model=TokenPair)
async def refresh_tokens(
    db: DBDep,
    request: Request,
    response: Response,
    body: RefreshIn | None = Body(default=None),
):
    token = extract_refresh_token(request, body)

    pair = await AuthServices(db).refresh(token)

    response.set_cookie(
        "refresh_token",
        pair.refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        path="/",
        max_age=settings.REFRESH_EXPIRES,
    )

    return pair


@router.post("/register", status_code=201, response_model=User)
async def register_user(
    db: DBDep,
    redis: RedisDep,
    data: UserAdd,
):
    user = await AuthServices(db).register(data)

    await VerifyService(db, redis).start(user.email)

    return user


@router.post("/login", response_model=TokenPair)
async def login_user(
        db: DBDep,
        data: LoginIn,
        request: Request,
        response: Response
):
    ua = request.headers.get("user-agent")
    ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or (
        request.client.host if request.client else None
    )

    pair = await AuthServices(db).login(data, user_agent=ua, ip=ip)

    response.set_cookie(
        "refresh_token",
        pair.refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        path="/",
        max_age=settings.REFRESH_EXPIRES,
    )

    return pair
