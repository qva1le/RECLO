from pydantic import BaseModel
from sqlalchemy import insert

from src.repositories.mappers.base import DataMapper


class BaseRepository:

    model = None
    schema: DataMapper = None

    def __init__(self, session, mapper):
        self.session = session
        self.mapper = mapper


    # async def add(self, data: BaseModel):
    #     try:
    #         payload = data.model_dump(exclude_unset=True,exclude_none=True)
    #         stmt = insert(self.model).values(**payload).returning(self.model)
    #         res = await self.session.execute(stmt)
    #         model = res.scalars().one()
    #         return self.mapper.map_to_domain_entity(model)
    #         if model is None:
    #             raise Ob
