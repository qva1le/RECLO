from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.auth import router as router_auth
from src.api.verify import router as router_verify
from src.api.seller_applications import router as router_seller_applications
from src.api.admin_seller_applications import router as router_seller_applications_admin
from src.api.shops import router as router_shops
from src.api.admin_shops import router as router_shop_admin
from src.config import settings
from src.connectors.redis_connector import RedisManager
from src.exceptions import AppException, to_http


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---- startup ----
    redis_manager = RedisManager(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=0,
    )
    await redis_manager.connect()
    await redis_manager.redis.ping()

    app.state.redis_manager = redis_manager
    try:
        yield
    finally:
        # ---- shutdown ----
        await redis_manager.close()


app = FastAPI(lifespan=lifespan)

# 👇 добавляем CORS прямо после создания app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # твой Vite frontend
    allow_credentials=True,  # нужно для cookie/refresh токенов
    allow_methods=["*"],
    allow_headers=["*"],
)

# роуты
app.include_router(router_auth)
app.include_router(router_verify)
app.include_router(router_seller_applications)
app.include_router(router_seller_applications_admin)
app.include_router(router_shops)
app.include_router(router_shop_admin)


# единый маппинг доменных исключений в HTTP
@app.exception_handler(AppException)
async def app_exception_handler(_, exc: AppException):
    raise to_http(exc)


# healthcheck
@app.get("/healthz")
async def healthz():
    return {"ok": True}

#ЗАПУСК
# uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
