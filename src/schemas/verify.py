from pydantic import BaseModel, EmailStr, constr


class VerifyStartIn(BaseModel):
    email: EmailStr

class VerifyConfirmIn(BaseModel):
    email: EmailStr
    code: constr(pattern=r"^\d{6}$")

