from fastapi import FastAPI

from src.config import settings
from src.api.auth import router as router_auth
from src.exceptions import AppException, to_http

print(f"{settings.DB_URL=}")

app = FastAPI()

# Подключаем роуты
app.include_router(router_auth)

@app.exception_handler(AppException)
async def app_exception_handler(_, exc: AppException):
    raise to_http(exc)