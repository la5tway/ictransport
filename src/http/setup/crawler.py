from logging import Logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.infra.mosday.service import (
    CrawlerConfig,
    MosDayApi,
    MosDayParser,
    MosDayService,
)


def setup_crawler(
    config: CrawlerConfig,
    session_maker: async_sessionmaker[AsyncSession],
    logger: Logger,
):
    return MosDayService(
        MosDayApi(),
        MosDayParser(),
        session_maker,
        config,
        logger,
    )
