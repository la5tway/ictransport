from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession


class SessionRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session


class CoreRepo:
    def __init__(self, conn: AsyncConnection) -> None:
        self._conn = conn
