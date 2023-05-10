from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from src.infra.db.repositories import NewsRepo

from .db import get_connection_factory, get_news_repository, get_session_factory


def setup_dependencies(
    engine: AsyncEngine,
    session_maker: async_sessionmaker[AsyncSession],
):
    return {
        AsyncEngine: lambda: engine,
        AsyncConnection: get_connection_factory(engine),
        AsyncSession: get_session_factory(session_maker),
        NewsRepo: get_news_repository,
    }
