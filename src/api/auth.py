from typing import Annotated

from fastapi import APIRouter
from fastapi.security import HTTPBasic, HTTPBasicCredentials

router = APIRouter(prefix="", tags=["Auth"])

@router.get("/me")
async def me():
    ...

@router.get("/logout")
async def logout_user():
    ...

@router.post("/register")
async def register_user():
    ...

@router.post("/login")
async def login_user():
    ...