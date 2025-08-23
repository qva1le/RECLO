from src.models.users import UsersOrm
from src.repositories.mappers.base import DataMapper
from src.schemas.users import User


class UsersDataMapper(DataMapper):
    db_model = UsersOrm
    schema = User