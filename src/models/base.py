from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Any
from ..config import settings

engine = create_async_engine(
    settings.db.uri,
    future=True,
    echo=settings.server.debug,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow,
)

async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

Base = declarative_base()


async def get_db() -> Any:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()
