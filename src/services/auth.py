from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.util import deprecated

from src.exceptions import AlreadyExistsException
from src.models.users import UsersOrm
from src.schemas.users import UserAdd, User
from src.services.base import BaseService

from src.core.security import hash_password

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Literal, cast
import uuid

import jwt
from passlib.context import CryptContext

from src.core.security import hash_password
from src.schemas.users import User as UserSchema
from src.utils.exceptions import ObjectNotFoundException


class AuthServices(BaseService):
    async def register(self, data: UserAdd) -> dict:
        email_norm = data.email.lower().strip()

        exists = await self.db.users.get_by_email(email_norm)
        if exists:
            raise AlreadyExistsException("User with this email already exists")

        hashed = hash_password(data.password)

        try:
            created = cast(UsersOrm, await self.db.users.add({
                "name": data.name.strip(),
                "email": email_norm,
                "password": hashed,
            }))
            await self.db.commit()

        except IntegrityError:
            await self.db.rollback()
            raise AlreadyExistsException("User with this email already exists")

        return UserSchema.model_validate(created)

