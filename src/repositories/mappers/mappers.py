from src.models.sessions import SessionsOrm
from src.models.users import UsersOrm
from src.repositories.mappers.base import DataMapper
from src.schemas.sessions import Session
from src.schemas.users import User


class UsersDataMapper(DataMapper):
    db_model = UsersOrm
    schema = User

class SessionsDataMapper(DataMapper):
    db_model = SessionsOrm
    schema = Session