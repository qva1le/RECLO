from sqlalchemy.util import deprecated

from src.schemas.users import UserAdd
from src.services.base import BaseService

from src.core.security import hash_password

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Literal
import uuid

import jwt
from passlib.context import CryptContext

class AuthService(BaseService):
    async def register(self, data: UserAdd):
        ...

