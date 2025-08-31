from pydantic import BaseModel
from sqlalchemy import insert, update, delete, select
from sqlalchemy.exc import IntegrityError, NoResultFound, MultipleResultsFound

from src.repositories.mappers.base import DataMapper
from src.utils.exceptions import map_integrity_error, NotFound, RepositoryError


class BaseRepository:

    model = None
    schema: DataMapper = None

    def __init__(self, session, mapper):
        self.session = session
        self.mapper = mapper

    async def get_one_or_none(self, *filter, **filter_by):
        stmt = select(self.model).filter(*filter).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        model = res.scalars().one_or_none()
        return None if model is None else self.mapper.map_to_domain_entity(model)

    async def get_one(self, *filter, **filter_by):
        try:
            stmt = select(self.model).filter(*filter).filter_by(**filter_by)
            res = await self.session.execute(stmt)
            model = res.scalars().one()
            return self.mapper.map_to_domain_entity(model)
        except NoResultFound:
            raise NotFound("Object not found")
        except MultipleResultsFound:
            raise RepositoryError("Excepted exactly one row, got many")

    async def add(self, data: BaseModel):
        try:
            payload = data.model_dump(exclude_unset=True,exclude_none=True)
            stmt = insert(self.model).values(**payload).returning(self.model)
            res = await self.session.execute(stmt)
            model = res.scalars().one()
            return self.mapper.map_to_domain_entity(model)
        except IntegrityError as ex:
            raise map_integrity_error(ex)

    async def add_bulk(self, data: list[BaseModel]):
        if not data:
            return []
        try:
            rows = [d.model_dimp(exclude_unset=True, exclude_none=True) for d in data]
            res = await self.session.execute(
                insert(self.model).values(rows).returning(self.model)
            )
            return [self.mapper.map_to_domain_entity(m) for m in res.scalars().all()]
        except IntegrityError as ex:
            raise map_integrity_error(ex)

    async def edit(self, data: BaseModel, *, exclude_unset: bool = False, **filter_by) -> None:
        try:
            values = data.model_dump(exclude_unset=True, exclude_none=True)
            if not values:
                return
            stmt = (
                update(self.model)
                .filter_by(**filter_by)
                .values(**values)
            )
            res = await self.session.execute(stmt)
            if res.rowcount == 0:
                raise NotFound("Object to update not found")
        except IntegrityError as ex:
            raise map_integrity_error(ex)

    async def delete(self, **filter_by) -> None:
        try:
            stmt = delete(self.model).filter_by(**filter_by)
            res = await self.session.execute(stmt)
            if res.rowcount == 0:
                raise NotFound("Object to delete not found")
        except  IntegrityError as ex:
            raise map_integrity_error(ex)





