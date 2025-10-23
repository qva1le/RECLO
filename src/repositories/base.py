# src/repositories/base.py
from typing import Any, Mapping, Union, Iterable, List
from pydantic import BaseModel
from sqlalchemy import insert, update, delete, select
from sqlalchemy.exc import IntegrityError, NoResultFound, MultipleResultsFound

from src.repositories.mappers.base import DataMapper
from src.utils.exceptions import map_integrity_error, NotFound, RepositoryError


class BaseRepository:
    model = None
    schema: DataMapper = None

    def __init__(self, session, mapper: DataMapper):
        self.session = session
        self.mapper = mapper

    # ---- helpers ------------------------------------------------------------
    @staticmethod
    def _to_payload(data: Union[BaseModel, Mapping[str, Any]], *, exclude_unset: bool = True) -> dict:
        """
        Унифицирует вход: принимает либо Pydantic-модель (v2/v1), либо dict/Mapping.
        Удаляет None по умолчанию, и (опционально) неустановленные поля.
        """
        if isinstance(data, BaseModel):
            # Pydantic v2
            if hasattr(data, "model_dump"):
                return data.model_dump(exclude_unset=exclude_unset, exclude_none=True)
            # Pydantic v1 fallback
            return data.dict(exclude_unset=exclude_unset, exclude_none=True)

        if isinstance(data, Mapping):
            # фильтруем None
            return {k: v for k, v in data.items() if v is not None}

        raise TypeError(f"Unsupported payload type: {type(data)}. Expected BaseModel or Mapping.")

    @staticmethod
    def _to_rows(data: Iterable[Union[BaseModel, Mapping[str, Any]]], *, exclude_unset: bool = True) -> List[dict]:
        return [BaseRepository._to_payload(d, exclude_unset=exclude_unset) for d in data]

    # ---- queries ------------------------------------------------------------
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
            raise RepositoryError("Expected exactly one row, got many")

    async def add(self, data: Union[BaseModel, Mapping[str, Any]]):
        try:
            payload = self._to_payload(data, exclude_unset=True)
            stmt = insert(self.model).values(**payload).returning(self.model)
            res = await self.session.execute(stmt)
            model = res.scalars().one()
            return self.mapper.map_to_domain_entity(model)
        except IntegrityError as ex:
            raise map_integrity_error(ex)

    async def add_bulk(self, data: list[Union[BaseModel, Mapping[str, Any]]]):
        if not data:
            return []
        try:
            rows = self._to_rows(data, exclude_unset=True)  # <-- фикс: и BaseModel, и dict; плюс опечатка
            res = await self.session.execute(
                insert(self.model).values(rows).returning(self.model)
            )
            return [self.mapper.map_to_domain_entity(m) for m in res.scalars().all()]
        except IntegrityError as ex:
            raise map_integrity_error(ex)

    async def edit(
            self,
            data: Union[BaseModel, Mapping[str, Any]],
            *,
            exclude_unset: bool = False,
            return_entity: bool = False,
            **filter_by,
    ):
        try:
            values = self._to_payload(data, exclude_unset=exclude_unset)
            if not values:
                return None
            stmt = update(self.model).filter_by(**filter_by).values(**values)
            if return_entity:
                stmt = stmt.returning(self.model)
                res = await self.session.execute(stmt)
                model = res.scalars().one_or_none()
                if model is None:
                    raise NotFound("Object to update not found")
                return self.mapper.map_to_domain_entity(model)
            else:
                res = await self.session.execute(stmt)
                if res.rowcount == 0:
                    raise NotFound("Object to update not found")
                return None
        except IntegrityError as ex:
            raise map_integrity_error(ex)

    async def delete(self, **filter_by) -> None:
        try:
            stmt = delete(self.model).filter_by(**filter_by)
            res = await self.session.execute(stmt)
            if res.rowcount == 0:
                raise NotFound("Object to delete not found")
        except IntegrityError as ex:
            raise map_integrity_error(ex)
