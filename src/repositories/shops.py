from select import select

from fastapi import HTTPException

from src.models.shops import ShopsOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.base import DataMapper
from src.repositories.mappers.mappers import ShopsDataMapper
from src.schemas.enums import ShopStatus


class ShopsRepository(BaseRepository):
    model = ShopsOrm
    mapper: DataMapper = ShopsDataMapper

