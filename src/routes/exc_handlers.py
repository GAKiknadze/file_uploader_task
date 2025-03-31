from fastapi import Request, status
from fastapi.responses import JSONResponse

from ..services.exceptions import (
    AccessDeniedExc,
    BadRequestExc,
    NotAuthorizedExc,
    ObjectNotFoundExc,
    SomethingWrongExc,
)


async def bad_request_exc_handler(
    request: Request, exc: BadRequestExc | Exception
) -> JSONResponse:
    return JSONResponse(
        {"msg": str(exc)},
        status_code=status.HTTP_400_BAD_REQUEST,
    )


async def not_authorized_exc_handler(
    request: Request, exc: NotAuthorizedExc | Exception
) -> JSONResponse:
    return JSONResponse(
        {"msg": str(exc)},
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


async def access_denied_exc_handler(
    request: Request, exc: AccessDeniedExc | Exception
) -> JSONResponse:
    return JSONResponse(
        {"msg": str(exc)},
        status_code=status.HTTP_403_FORBIDDEN,
    )


async def object_not_found_exc_handler(
    request: Request, exc: ObjectNotFoundExc | Exception
) -> JSONResponse:
    return JSONResponse(
        {"msg": str(exc)},
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def all_exc_handler(
    request: Request, exc: SomethingWrongExc | Exception
) -> JSONResponse:
    return JSONResponse(
        {"msg": str(exc)},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
