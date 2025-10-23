import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select, update

from src.models.sessions import SessionsOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.base import DataMapper
from src.repositories.mappers.mappers import SessionsDataMapper


class SessionsRepository(BaseRepository):
    model = SessionsOrm
    schema: DataMapper = SessionsDataMapper

    async def create_session(
            self,
            *,
            user_id: int,
            jti: str,
            user_agent: str | None,
            ip: str | None,
            expires_at: datetime
    ) -> SessionsOrm:
        obj = SessionsOrm(
            user_id=user_id, jti=jti, user_agent=user_agent, ip=ip, expires_at=expires_at
        )
        self.session.add(obj)
        await self.session.flush()
        return obj

    #СОЗДАЁТ СЕССИЮ

    async def get_session(self, session_id: uuid.UUID) -> Optional[SessionsOrm]:
        stmt = select(SessionsOrm).filter(SessionsOrm.id == session_id)
        return await self.session.scalar(stmt)

    #ВОЗВРАЩАЕТ СЕССИЮ

    async def get_by_active_user(self, user_id: int):
        stmt = select(SessionsOrm).filter(
            SessionsOrm.user_id == user_id,
            SessionsOrm.revoked.is_(False)
        )
        result =  await self.session.scalars(stmt)
        return result.all()

    #ВОЗВРАЩАЕТ ВСЕ СЕССИИИ

    async def rotate_jti(self, session_id: uuid.UUID, new_jti: str, *, now: datetime) -> None:
        stmt = (
            update(SessionsOrm)
            .filter(SessionsOrm.id == session_id, SessionsOrm.revoked.is_(False))
            .values(jti=new_jti, last_used_at=now)
        )
        await self.session.execute(stmt)

    #МОЖЕТ ОБНОВИТЬ СЕССИЮ, ЕСЛИ ОНА НЕ ОТОЗВАНА

    async def revoke(self, session_id: uuid.UUID) -> None:
        stmt = (
            update(SessionsOrm).filter(SessionsOrm.id == session_id)
            .values(revoked=True)
        )
        await self.session.execute(stmt)

    #ДЕЛАЕТ ТОКЕН СЕССИИ НЕДЕЙСТВИТЕЛЬНЫМ

    async def revoke_all_for_user(self, user_id: int) -> None:
        stmt = update(SessionsOrm).filter(SessionsOrm.user_id == user_id).values(revoked=True)
        await self.session.execute(stmt)

    # ВЫЙТИ СО ВСЕХ УСТРОЙСТВ


