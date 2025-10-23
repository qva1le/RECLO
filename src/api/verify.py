from fastapi import APIRouter, Body

from src.api.dependencies import DBDep, RedisDep
from src.exceptions import AppException, to_http
from src.services.verify import VerifyService

router = APIRouter(prefix="/verify")

@router.post("/start")
async def start_verification(db: DBDep, redis: RedisDep, email: str = Body(..., embed= True)):
    try:
        await VerifyService(db, redis).start(email)
        return{"detail": "Код верификации отправлен"}
    except AppException as e:
        raise to_http(e)

@router.post("/confirm")
async def confirm_verification(db: DBDep, redis: RedisDep, email: str = Body(...), code: str = Body(...)):
    try:
        service = VerifyService(db, redis)
        await service.confirm(email, code)
        return {"detail": "Email подтверждён"}
    except AppException as e:
        raise to_http(e)