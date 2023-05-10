import asyncio
import logging

import uvicorn

from src.infra.config_loader import load_config
from src.infra.log import setup_logging
from src.infra.tasks import Tasks

from . import app_name
from .config import Config
from .setup import (
    setup_api,
    setup_crawler,
    setup_db,
    setup_dependencies,
    setup_orm_mapping,
)


async def main_async():
    config = load_config(Config)

    log_level = "DEBUG" if config.app.is_dev else "INFO"
    logger = logging.getLogger(app_name)
    setup_logging(app_name, log_level)
    setup_orm_mapping()

    tasks = Tasks()

    engine, session_maker = setup_db(config)
    await tasks.build_add(engine, stop=engine.dispose())

    crawler = setup_crawler(config.crawler, session_maker, logger)
    await crawler.prestart()
    await tasks.add(crawler)

    dependencies_overrides = setup_dependencies(engine, session_maker)
    api = setup_api(config, dependencies_overrides)

    server_config = uvicorn.Config(
        app=api,
        host=config.http.host,
        port=config.http.port,
        log_level=log_level.lower(),
        log_config=None,
        server_header=False,
        date_header=False,
    )
    server = uvicorn.Server(config=server_config)
    sockets = [server_config.bind_socket()]
    try:
        await server.serve(sockets)
    finally:
        await server.shutdown(sockets)
        await tasks.stop()


def main_sync():
    import uvloop

    uvloop.install()
    asyncio.run(main_async())
