from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Literal
import uuid

import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

class TokenType:
    ACCESS: Literal["access"] = "access"
    REFRESH: Literal["refresh"] = "refresh"

def create_jwt(
        *,
        subject: str | int,
        token_type: Literal["access", "refresh"],
        secret_key: str,
        algorithm: str = "HS256",
        expires_delta: timedelta,
        extra_claims: Dict[str, Any] | None = None
) -> str:
    now = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {
        "sub": str(subject),
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "jti": str(uuid.uuid4())
    }

    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, secret_key, algorithm=algorithm)

def decode_jwt(token: str, *, secret_key: str, algorithms: list[str]) -> Dict[str, Any]:
    return jwt.decode(token, secret_key, algorithms=algorithms)


