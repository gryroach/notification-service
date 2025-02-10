# stdlib
from collections.abc import AsyncGenerator

# thirdparty
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# project
from core.config import settings

engine = create_async_engine(settings.database_dsn, echo=settings.echo_queries, future=True)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Возвращает асинхронную сессию базы данных."""
    async with async_session() as session:
        yield session
