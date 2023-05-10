import asyncio
from datetime import timedelta
from logging import Logger

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.constants import TAGS_LIST
from src.domain.news.models import NewsEntry
from src.infra.db.repositories.news import NewsRepo
from src.utils.dt import now

from .api import MosDayApi
from .config import CrawlerConfig
from .parser import MosDayParser


class MosDayService:
    def __init__(
        self,
        api: MosDayApi,
        parser: MosDayParser,
        session_maker: async_sessionmaker[AsyncSession],
        config: CrawlerConfig,
        logger: Logger,
    ) -> None:
        self._api = api
        self._parser = parser
        self._session_maker = session_maker
        self._config = config
        self._logger = logger.getChild(type(self).__name__)
        self._task = None

    async def start(self):
        await self._api.start()
        self._task = asyncio.create_task(self._run())

    async def stop(self):
        await self._api.stop()
        if self._task:
            self._task.cancel()

    async def prestart(self):
        async with self._session_maker() as session:
            news_repo = NewsRepo(session)
            news_xml = await self._api.get_news()
            latest_news_id = self._parser.extract_latest_news_id(news_xml)
            latest_news_id_in_db = await news_repo.get_latest_news_id()
            if latest_news_id_in_db is None or (
                latest_news_id is not None and latest_news_id_in_db < latest_news_id
            ):
                total = len(TAGS_LIST)
                for idx, tag in enumerate(TAGS_LIST, 1):
                    self._logger.info(f"[{idx} / {total}] Preprocess tag `{tag}`")
                    try:
                        await self._execute_by_tag(tag, news_repo)
                    except Exception:
                        self._logger.exception(f"[{idx} / {total}][FAILED] Preprocess tag `{tag}`")
                        await session.rollback()
                    else:
                        await session.commit()
                        self._logger.info(f"[{idx} / {total}][SUCCESS] Preprocess tag `{tag}`")

    async def _run(self):
        while True:
            session = self._session_maker()
            try:
                news_repo = NewsRepo(session)
                news_xml = await self._api.get_news()
                latest_news_id = self._parser.extract_latest_news_id(news_xml)
                latest_news_id_in_db = await news_repo.get_latest_news_id()
                if latest_news_id_in_db is None or (
                    latest_news_id is not None and latest_news_id_in_db < latest_news_id
                ):
                    for news_entry in self._parser.parse_news_from_rss(
                        news_xml, latest_news_id_in_db
                    ):
                        if await news_repo.exists_by_id(news_entry.id):
                            continue
                        news_detail_html = await self._api.get_news_detail(
                            news_entry.id
                        )
                        tags = self._parser.extract_tags_from_detail(news_detail_html)
                        if not tags:
                            continue
                        await news_repo.bulk_create(
                            *(
                                NewsEntry(
                                    id=news_entry.id,
                                    tag=tag,
                                    title=news_entry.title,
                                    preview_url=news_entry.preview_url,
                                    pub_date=news_entry.pub_date,
                                    parsed_date=news_entry.parsed_date,
                                )
                                for tag in tags
                            )
                        )
                        await session.commit()
            finally:
                await session.close()
            next_run = now() + timedelta(seconds=self._config.delay_seconds)
            self._logger.info(f"Sleeping {self._config.delay_seconds} seconds. Next run in {next_run}")
            await asyncio.sleep(self._config.delay_seconds)

    async def _execute_by_tag(self, tag: str, news_repo: NewsRepo):
        latest_news_id = await news_repo.get_latest_news_id_by_tag(tag)
        if latest_news_id:
            await self._execute_by_tag_and_id(tag, news_repo, latest_news_id)
        else:
            await self._execute_by_tag_without_id(tag, news_repo)

    async def _execute_by_tag_and_id(
        self,
        tag: str,
        news_repo: NewsRepo,
        latest_news_id: str,
    ):
        i = 1
        id_ = None
        tag_ = tag
        while id_ != latest_news_id:
            if i > 1:
                tag_ = f"{tag}_{i}"
            news_html = await self._api.get_news_by_tag(tag_)
            news_entries = self._parser.parse_news(news_html, tag, latest_news_id)
            if not news_entries:
                return
            id_ = news_entries[-1].id
            await news_repo.bulk_create(*news_entries)
            i += 1

    async def _execute_by_tag_without_id(
        self,
        tag: str,
        news_repo: NewsRepo,
    ):
        i = 1
        dt = now()
        target_dt = dt - timedelta(self._config.parse_days)
        tag_ = tag
        while dt > target_dt:
            if i > 1:
                tag_ = f"{tag}_{i}"
            news_html = await self._api.get_news_by_tag(tag_)
            news_entries = self._parser.parse_news(news_html, tag)
            if not news_entries:
                return
            dt = news_entries[-1].pub_date
            await news_repo.bulk_create(*news_entries)
            i += 1
