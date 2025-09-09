from typing import Annotated

from fastapi import APIRouter
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.exc import IntegrityError

from src.api.dependencies import DBDep
from src.exceptions import to_http, AlreadyExistsException, AppException
from src.schemas.users import UserAdd
from src.services.auth import AuthServices

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/me")
async def me():
    ...

@router.get("/logout")
async def logout_user():
    ...

@router.post("/register", status_code=201)
async def register_user(db: DBDep, data: UserAdd):
    try:
        return await AuthServices(db).register(data)
    except IntegrityError:
        raise to_http(AlreadyExistsException("Пользователь с таким email уже существует"))
    except AppException as e:
        raise to_http(e)

@router.post("/login")
async def login_user():
    ...