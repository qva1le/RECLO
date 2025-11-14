from src.repositories.mappers.mappers import UsersDataMapper, SessionsDataMapper, ShopsDataMapper
from src.repositories.sessions import SessionsRepository
from src.repositories.shops import ShopsRepository
from src.repositories.users import UsersRepository


class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()

        self.users = UsersRepository(self.session, mapper=UsersDataMapper)
        self.sessions = SessionsRepository(self.session, mapper=SessionsDataMapper)
        self.shops = ShopsRepository(self.session, mapper=ShopsDataMapper)

        return self

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()