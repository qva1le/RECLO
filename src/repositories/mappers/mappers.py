from src.models.products import ProductsOrm
from src.models.sessions import SessionsOrm
from src.models.shops import ShopsOrm
from src.models.users import UsersOrm
from src.repositories.mappers.base import DataMapper
from src.schemas.products import ProductPublic
from src.schemas.sessions import Session
from src.schemas.shops import ShopOut
from src.schemas.users import User


class UsersDataMapper(DataMapper):
    db_model = UsersOrm
    schema = User

class SessionsDataMapper(DataMapper):
    db_model = SessionsOrm
    schema = Session

class ShopsDataMapper(DataMapper):
    db_model = ShopsOrm
    schema = ShopOut

class ProductsDataMapper(DataMapper):
    db_model = ProductsOrm
    schema = ProductPublic

