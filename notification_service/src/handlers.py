# stdlib
from collections.abc import Callable, Coroutine
from typing import Any

# thirdparty
from fastapi import Request
from sqlalchemy.exc import IntegrityError
from starlette import status
from starlette.responses import JSONResponse, Response

# project
from exceptions.auth_exceptions import AuthError
from exceptions.db import ForeignKeyNotExistsError


async def auth_exception_handler(_: Request, exc: AuthError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
    )


async def http_error_handler(_: Request, exc: Exception) -> JSONResponse:
    """Обработчик HTTP ошибок."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )


async def foreign_key_error_handler(_: Request, exc: ForeignKeyNotExistsError) -> JSONResponse:
    """Обработчик ошибок внешнего ключа."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)},
    )


async def integrity_error_handler(_: Request, exc: IntegrityError) -> JSONResponse:
    """Обработчик ошибок внешнего ключа."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


exception_handlers: (
    dict[
        int | type[Exception],
        Callable[[Request, Any], Coroutine[Any, Any, Response]],
    ]
    | None
) = {
    AuthError: auth_exception_handler,
    ForeignKeyNotExistsError: foreign_key_error_handler,
    IntegrityError: integrity_error_handler,
}
