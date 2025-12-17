# src/services/verify.py
import secrets
import re
import logging
from datetime import datetime, timezone  # можно убрать, если verified_at не используем

from src.config import settings
from src.connectors.redis_connector import RedisManager
from src.exceptions import (
    ObjectNotFoundException,
    AlreadyExistsException,
    AuthenticationException,
    AppException,
)
from src.services.base import BaseService
from src.services.email import EmailService
from src.utils.exceptions import NotFound as RepoNotFound
from src.schemas.enums import UserStatus  # если хочешь обновлять статус

logger = logging.getLogger(__name__)

def _gen_code(n: int) -> str:
    return str(secrets.randbelow(10**n)).zfill(n)

class VerifyService(BaseService):
    def __init__(self, db, redis_manager: RedisManager):
        super().__init__(db)
        self.redis = redis_manager

    async def start(self, email: str) -> None:
        email = email.lower().strip()
        user = await self.db.users.get_by_email(email)
        if not user:
            raise ObjectNotFoundException("User not found")
        # было: getattr(user, "is_verified", False)
        if user.status != UserStatus.pending_email:
            raise AuthenticationException("Верификация не пройдена")

        key_code = f"verify:code:{email}"
        key_rl = f"verify:rl:{email}"

        ttl_left = await self.redis.ttl(key_rl)
        if ttl_left and ttl_left > 0:
            raise AuthenticationException("Too many requests. Try later")

        code = _gen_code(settings.VERIFY_CODE_LENGTH)
        await self.redis.set(key_code, code, expire=settings.VERIFY_CODE_TTL_SECONDS)

        try:
            if getattr(settings, "DEBUG", False):
                print(f"[DEV] verify code for {email}: {code}")
            else:
                await EmailService(self.db).verification_code(email, code)
        except AppException:
            await self.redis.delete(key_code)
            raise

        await self.redis.set(key_rl, "1", expire=settings.VERIFY_SEND_COOLDOWN_SECONDS)

    async def confirm(self, email: str, code: str) -> None:
        email = email.lower().strip()
        key_code = f"verify:code:{email}"

        clean_code = re.sub(r"\D", "", code or "")
        if not clean_code:
            raise AuthenticationException("Неверный формат кода")

        saved_code = await self.redis.get(key_code)
        if not saved_code:
            raise ObjectNotFoundException("Верификационный код недействителен или истёк")
        if saved_code != clean_code:
            raise AuthenticationException("Верификационный код недействителен")

        user = await self.db.users.get_by_email(email)
        if not user:
            raise ObjectNotFoundException("Пользователь не найден")
        if user.status != UserStatus.pending_email:
            return
        # подготавливаем апдейт под твою схему
        update_values = {"email_verified": True}
        # если хочешь сразу активировать
        try:
            if hasattr(UserStatus, "active") and getattr(user, "status", None) == UserStatus.pending_email:
                update_values["status"] = UserStatus.active
        except Exception:
            # если enum без active — просто игнорируем
            pass

        try:
            await self.db.users.edit(update_values, email=email)  # апдейт по email
            await self.db.commit()
            await self.redis.delete(key_code)
        except RepoNotFound:
            raise ObjectNotFoundException("Пользователь не найден")
        except Exception as e:
            logger.exception("Verify confirm failed for %s", email)
            raise AppException(f"Verify confirm failed: {e!s}")
