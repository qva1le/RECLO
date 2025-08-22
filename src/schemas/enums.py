from enum import Enum


class UserStatus(str, Enum):
    pending_email = "pending_email"
    active = "active"
    blocked = "blocked"
    deleted = "deleted"

class CodeStatus(str, Enum):
    email_verify = "email_verify"
    password_reset = "password_reset"