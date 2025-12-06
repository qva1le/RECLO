from src.models.products import ProductsOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.base import DataMapper
from src.repositories.mappers.mappers import ProductsDataMapper


class ProductsRepository(BaseRepository):
    model = ProductsOrm
    mapper: DataMapper = ProductsDataMapper

