

class AppError(Exception):
    code: str = "app_error"
    status_code: int = 400

    def __init__(self, message: str | None = None):
        super().__init__(message or type(self).__name__)
        self.message = self.args[0]


class NotFound(AppError):
    pass

class ObjectNotFoundException(NotFound):
    pass

class Conflict(AppError):
    pass

class RepositoryError(AppError):
    pass

class Unauthorized(AppError):
    status_code = 401

from sqlalchemy.exc import IntegrityError

_PG_UNIQUE = "23505"

def map_integrity_error(exc: IntegrityError) -> AppError:
    sqlstate = getattr(getattr(exc, "orig", None), "sqlstate", None)
    if sqlstate == _PG_UNIQUE:
        return Conflict("Already exists")
    return RepositoryError("Integrity Error")