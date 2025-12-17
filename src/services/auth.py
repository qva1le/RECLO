# src/services/auth.py
import uuid
from datetime import datetime, timedelta, timezone
from typing import cast

from sqlalchemy.exc import IntegrityError

from src.config import settings
from src.exceptions import (
    AlreadyExistsException,
    AuthenticationException,
    AuthorizationException,
)
from src.models.users import UsersOrm
from src.schemas.enums import UserStatus
from src.schemas.users import UserAdd, LoginIn, TokenPair
from src.services.base import BaseService
from src.core.security import hash_password, verify_password, create_jwt, decode_jwt
from src.schemas.users import User as UserSchema


class AuthServices(BaseService):
    async def register(self, data: UserAdd) -> UserSchema:
        email_norm = data.email.lower().strip()

        exists = await self.db.users.get_by_email(email_norm)
        if exists:
            raise AlreadyExistsException("Пользователь с таким email уже существует")

        hashed = hash_password(data.password)

        try:
            created = cast(
                UsersOrm,
                await self.db.users.add(
                    {
                        "name": data.name.strip(),
                        "email": email_norm,
                        "password_hash": hashed,
                        "email_verified": False,
                        "status": UserStatus.pending_email
                    }
                ),
            )
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise AlreadyExistsException("Пользователь с таким email уже существует")

        return UserSchema.model_validate(created)

    async def login(self, data: LoginIn, *, user_agent: str | None, ip: str | None) -> TokenPair:
        email = data.email.lower().strip()
        user: UsersOrm | None = await self.db.users.get_by_email(email)

        if not user:
            raise AuthenticationException("Invalid email or password")

        if user.status != UserStatus.active:
            raise AuthenticationException("Пользователь не активен")

        if not verify_password(data.password, user.password_hash):
            raise AuthenticationException("Invalid email or password")

        refresh_jti = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        refresh_ttl = timedelta(seconds=settings.REFRESH_EXPIRES)

        session = await self.db.sessions.create_session(
            user_id=user.id,
            jti=refresh_jti,
            user_agent=user_agent,
            ip=ip,
            expires_at=now + refresh_ttl,
        )

        access = create_jwt(
            subject=user.id,
            token_type="access",
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            expires_delta=timedelta(seconds=settings.ACCESS_EXPIRES),
            extra_claims={"email": user.email},
        )

        refresh = create_jwt(
            subject=user.id,
            token_type="refresh",
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            expires_delta=refresh_ttl,
            extra_claims={"jti": refresh_jti, "sid": str(session.id)},
        )

        await self.db.commit()
        return TokenPair(access_token=access, refresh_token=refresh)

    async def refresh(self, refresh_token: str) -> TokenPair:
        payload = decode_jwt(
            refresh_token,
            secret_key=settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        if payload.get("type") != "refresh":
            raise AuthorizationException("Refresh token required")

        user_id = int(payload["sub"])
        sid = payload.get("sid")
        jti = payload.get("jti")

        if not sid or not jti:
            raise AuthenticationException("Invalid refresh token")

        user = await self.db.users.get(user_id)
        if not user or user.status != UserStatus.active:
            raise AuthenticationException("Пользователь не активен")

        session = await self.db.sessions.get(uuid.UUID(sid))
        if not session or session.user_id != user_id:
            raise AuthenticationException("Session not found")
        if session.revoked:
            raise AuthenticationException("Session revoked")
        if session.expires_at <= datetime.now(timezone.utc):
            raise AuthenticationException("Session expired")

        if session.jti != jti:
            await self.db.sessions.revoke_all_for_user(user_id)
            await self.db.commit()
            raise AuthenticationException("Refresh token reused")

        new_jti = str(uuid.uuid4())
        await self.db.sessions.rotate_jti(session.id, new_jti, now=datetime.now(timezone.utc))

        access = create_jwt(
            subject=user_id,
            token_type="access",
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            expires_delta=timedelta(seconds=settings.ACCESS_EXPIRES),
        )

        refresh = create_jwt(
            subject=user_id,
            token_type="refresh",
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            expires_delta=session.expires_at - datetime.now(timezone.utc),
            extra_claims={"jti": new_jti, "sid": str(session.id)},
        )

        await self.db.commit()
        return TokenPair(access_token=access, refresh_token=refresh)

    async def logout_current(self, refresh_token: str) -> None:
        payload = decode_jwt(
            refresh_token,
            secret_key=settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "refresh":
            raise AuthorizationException("Refresh token required")
        sid = payload.get("sid")
        if not sid:
            raise AuthenticationException("Invalid refresh token")
        await self.db.sessions.revoke(uuid.UUID(sid))
        await self.db.commit()

    async def logout_all(self, user_id: int) -> None:
        await self.db.sessions.revoke_all_for_user(user_id)
        await self.db.commit()
