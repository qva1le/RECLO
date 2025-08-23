from src.models.users import UsersOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.base import DataMapper
from src.repositories.mappers.mappers import UsersDataMapper


class UsersRepository(BaseRepository):
    model = UsersOrm
    schema: DataMapper = UsersDataMapper