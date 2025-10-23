# main.py
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from src.api.auth import router as router_auth
from src.api.verify import router as router_verify
from src.config import settings
from src.connectors.redis_connector import RedisManager
from src.exceptions import AppException, to_http

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---- startup ----
    redis_manager = RedisManager(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=0,  # при необходимости вынеси в settings (REDIS_DB), сейчас 0 по умолчанию в менеджере
    )
    await redis_manager.connect()
    # healthcheck — сразу вскрывает неверный хост/порт/ACL
    await redis_manager.redis.ping()

    app.state.redis_manager = redis_manager
    try:
        yield
    finally:
        # ---- shutdown ----
        await redis_manager.close()


app = FastAPI(lifespan=lifespan)

# роуты
app.include_router(router_auth)
app.include_router(router_verify)

# единый маппинг доменных исключений в HTTP
@app.exception_handler(AppException)
async def app_exception_handler(_, exc: AppException):
    raise to_http(exc)


# (опционально) healthcheck для оркестратора/инфры
@app.get("/healthz")
async def healthz():
    return {"ok": True}
