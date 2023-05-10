from aiohttp import ClientSession


class MosDayApi:
    def __init__(self) -> None:
        self._api = ClientSession(
            base_url="https://mosday.ru/",
        )

    async def start(self):
        ...

    async def stop(self):
        await self._api.close()

    async def get_news_by_tag(self, tag: str):
        response = await self._api.get(f"/news/tags.php?{tag}")
        response.raise_for_status()
        return await response.read()

    async def get_news(self):
        response = await self._api.get("/news/rss.xml")
        response.raise_for_status()
        return await response.read()

    async def get_tags(self):
        response = await self._api.get("/news/tags.php")
        response.raise_for_status()
        return await response.read()

    async def get_news_detail(self, news_id: str):
        print(f"{news_id=}")
        response = await self._api.get(f"/news/item.php?{news_id}")
        response.raise_for_status()
        return await response.read()
