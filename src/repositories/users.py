from typing import Optional

from sqlalchemy import select

from src.models.users import UsersOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.base import DataMapper
from src.repositories.mappers.mappers import UsersDataMapper


class UsersRepository(BaseRepository):
    model = UsersOrm
    schema: DataMapper = UsersDataMapper

    async def get_by_id(self, user_id: int) -> Optional[UsersOrm]:
        stmt = select(UsersOrm).filter(UsersOrm.id == user_id)
        return await self.session.scalar(stmt)

    async def get_by_email(self, email: str) -> Optional[UsersOrm]:
        stmt = select(UsersOrm).filter(UsersOrm.email == email)
        return await self.session.scalar(stmt)



