# stdlib
from collections.abc import Callable, Coroutine
from typing import Any

# thirdparty
from fastapi import Request
from starlette import status
from starlette.responses import JSONResponse, Response

# project
from exceptions.auth_exceptions import AuthError


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


exception_handlers: (
    dict[
        int | type[Exception],
        Callable[[Request, Any], Coroutine[Any, Any, Response]],
    ]
    | None
) = {
    AuthError: auth_exception_handler,
}
