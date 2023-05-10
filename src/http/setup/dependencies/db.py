from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from src.http.stub import Stub
from src.infra.db.repositories.news import NewsRepo


def get_connection_factory(engine: AsyncEngine):
    async def connection_factory() -> AsyncGenerator[AsyncConnection, None]:
        async with engine.connect() as conn:
            yield conn

    return connection_factory


def get_session_factory(maker: async_sessionmaker[AsyncSession]):
    async def session_factory() -> AsyncGenerator[AsyncSession, None]:
        async with maker() as session:
            yield session

    return session_factory


async def get_news_repository(session: AsyncSession = Depends(Stub(AsyncSession))):
    return NewsRepo(session)
