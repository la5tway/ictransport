from sqlalchemy.ext.asyncio import AsyncConnection

from src.http.stub import Stub
from src.infra.db.repositories import NewsRepo

StubAsyncConnection = Stub(AsyncConnection)
StubNewsRepo = Stub(NewsRepo)
