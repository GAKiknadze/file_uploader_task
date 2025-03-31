import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import exc, select

from .models.base import Base, engine
from .routes import auth, exc_handlers, file, user
from .services.exceptions import (
    AccessDeniedExc,
    BadRequestExc,
    NotAuthorizedExc,
    ObjectNotFoundExc,
    SomethingWrongExc,
)

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.execute(select(1))
            logger.info("Database initialized successfully")

    except exc.SQLAlchemyError as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise RuntimeError("Database connection error") from e


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await engine.dispose()


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(file.router, prefix="/file", tags=["file"])

app.add_exception_handler(BadRequestExc, exc_handlers.bad_request_exc_handler)
app.add_exception_handler(NotAuthorizedExc, exc_handlers.not_authorized_exc_handler)
app.add_exception_handler(AccessDeniedExc, exc_handlers.access_denied_exc_handler)
app.add_exception_handler(ObjectNotFoundExc, exc_handlers.object_not_found_exc_handler)
# app.add_exception_handler(SomethingWrongExc | Exception, exc_handlers.all_exc_handler)
