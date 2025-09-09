from src.models.sessions import SessionsOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.base import DataMapper
from src.repositories.mappers.mappers import SessionsDataMapper


class SessionsRepository(BaseRepository):
    model = SessionsOrm
    schema: DataMapper = SessionsDataMapper

