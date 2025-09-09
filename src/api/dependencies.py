from typing import Annotated, Optional

from authx import AuthXConfig
from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer

from src.config import settings
from src.core.security import decode_jwt
from src.database import async_session_maker
from src.exceptions import AuthorizationException, ObjectNotFoundException
from src.services.base import BaseService
from src.utils.db_manager import DBManager


async def get_current_user(db: BaseService, authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AuthorizationException("Missing access token")
    token = authorization.split(" ",1)[1].strip()

    try:
        payload = decode_jwt(token, seсret_key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except Exception:
        raise AuthorizationException("Invalid or expired token")

    if payload.get("type") != "access":
        raise AuthorizationException("Access token required")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthorizationException("Invalid token payload")

    user = await db.users.get_by_id(int(user_id))
    if not user:
        raise ObjectNotFoundException("User not found")
    return user

def db_manager():
    return DBManager(session_factory=async_session_maker)

async def get_db():
    async with db_manager() as db:
        yield db

DBDep = Annotated[DBManager, Depends(get_db)]