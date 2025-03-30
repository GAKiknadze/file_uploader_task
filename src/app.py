from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from .models.base import engine
from .routes import auth, exc_handlers, file, user
from .services.exceptions import (
    AccessDeniedExc,
    BadRequestExc,
    NotAuthorizedExc,
    ObjectNotFoundExc,
    SomethingWrongExc,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(file.router, prefix="/file", tags=["file"])

app.add_exception_handler(BadRequestExc, exc_handlers.bad_request_exc_handler)
app.add_exception_handler(NotAuthorizedExc, exc_handlers.not_authorized_exc_handler)
app.add_exception_handler(AccessDeniedExc, exc_handlers.access_denied_exc_handler)
app.add_exception_handler(ObjectNotFoundExc, exc_handlers.object_not_found_exc_handler)
app.add_exception_handler(SomethingWrongExc | Exception, exc_handlers.all_exc_handler)
