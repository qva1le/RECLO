from fastapi import HTTPException, status


class AppException(Exception):
    """
    Базовый класс для всех ошибок приложения.
    Можно наследовать для разных типов ошибок.
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ObjectNotFoundException(AppException):
    """Ошибка, если объект не найден в базе данных"""
    pass


class AlreadyExistsException(AppException):
    """Ошибка, если объект уже существует в базе данных"""
    pass


class AuthenticationException(AppException):
    """Ошибка аутентификации (неверный логин/пароль)"""
    pass


class AuthorizationException(AppException):
    """Ошибка авторизации (нет прав на выполнение действия)"""
    pass


# Удобные функции для возвращения HTTP ошибок в FastAPI
def to_http(exc: AppException) -> HTTPException:
    if isinstance(exc, AlreadyExistsException):
        return HTTPException(status_code=409, detail=exc.message or "Already exists")
    if isinstance(exc, AuthenticationException):
        return HTTPException(status_code=401, detail=exc.message or "Invalid credentials")
    if isinstance(exc, AuthorizationException):
        return HTTPException(status_code=403, detail=exc.message or "Forbidden")
    return HTTPException(status_code=400, detail=exc.message or "Bad request")
