from pydantic import BaseModel, EmailStr, ConfigDict


class UserAdd(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginIn:
    email: EmailStr
    password: str

class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class User(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)