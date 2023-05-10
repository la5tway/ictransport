from dataclasses import asdict
from datetime import timedelta

from sqlalchemy import exists, select
from sqlalchemy.dialects.postgresql import insert

from src.domain.news import NewsEntry
from src.infra.db.models import NewsEntryModel
from src.utils.dt import utcnow

from .base import SessionRepo


class NewsRepo(SessionRepo):
    async def get_by_tag(self, tag: str, day: int):
        stmt = (
            select(NewsEntry)
            .where(
                NewsEntryModel.tag == tag,
                NewsEntryModel.pub_date > utcnow() - timedelta(days=day),
            )
            .order_by(NewsEntryModel.pub_date.desc())
        )
        return (await self._session.scalars(stmt)).all()

    async def create(self, news_entry: NewsEntry):
        self._session.add(news_entry)
        return news_entry

    async def bulk_create(self, *news_entry: NewsEntry):
        stmt = (
            insert(NewsEntryModel)
            .values([asdict(entry) for entry in news_entry])
            .on_conflict_do_nothing()
        )
        await self._session.execute(stmt)

    async def exists_by_id(self, news_id: str):
        stmt = select(exists().where(NewsEntryModel.id == news_id))
        return await self._session.scalar(stmt) or False

    async def get_latest_news_id(self):
        stmt = (
            select(NewsEntryModel.id).order_by(NewsEntryModel.pub_date.desc()).limit(1)
        )
        return await self._session.scalar(stmt)

    async def get_latest_news_id_by_tag(self, tag: str):
        stmt = (
            select(NewsEntryModel.id)
            .where(NewsEntryModel.tag == tag)
            .order_by(NewsEntryModel.pub_date.desc())
        )
        return await self._session.scalar(stmt)
