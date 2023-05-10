import asyncio
from typing import Any, Awaitable, Protocol


class TaskProtocol(Protocol):
    async def start(self):
        ...

    async def stop(self):
        ...


class Task:
    def __init__(
        self,
        instance: Any,
        *,
        start: Awaitable[Any] | None = None,
        stop: Awaitable[Any] | None = None,
    ) -> None:
        self.instance = instance
        self._start = start
        self._stop = stop

    async def start(self):
        print(f"{type(self.instance).__name__} Started")
        if self._start:
            await self._start

    async def stop(self):
        print(f"{type(self.instance).__name__} Stopped")
        if self._stop:
            await self._stop

    def __str__(self) -> str:
        return type(self.instance).__name__


class Tasks:
    def __init__(self) -> None:
        self._items: list[tuple[asyncio.Task[Any], TaskProtocol]] = []

    async def add(self, task: TaskProtocol):
        self._items.append((asyncio.create_task(task.start()), task))

    async def build_add(
        self,
        instance: Any,
        *,
        start: Awaitable[Any] | None = None,
        stop: Awaitable[Any] | None = None,
    ):
        task = Task(instance, start=start, stop=stop)
        await self.add(task)

    async def stop(self):
        for task, service in self._items:
            await service.stop()
            task.cancel()
