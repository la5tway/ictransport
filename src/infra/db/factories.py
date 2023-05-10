import orjson
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def create_engine(url: str, echo: bool) -> AsyncEngine:
    engine = create_async_engine(
        url=url,
        echo=echo,
        json_serializer=orjson.dumps,
        json_deserializer=orjson.loads,
    )
    return engine


def create_session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )



