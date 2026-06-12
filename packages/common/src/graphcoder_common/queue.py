import asyncio
from collections import deque
from typing import Protocol

import redis.asyncio as redis


class JobQueue(Protocol):
    async def enqueue(self, job_id: str) -> None:
        pass

    async def dequeue(self, timeout_seconds: int) -> str | None:
        pass


class InMemoryJobQueue:
    def __init__(self) -> None:
        self._items: deque[str] = deque()

    async def enqueue(self, job_id: str) -> None:
        self._items.append(job_id)

    async def dequeue(self, timeout_seconds: int) -> str | None:
        if self._items:
            return self._items.popleft()

        await asyncio.sleep(timeout_seconds)
        return None


class RedisJobQueue:
    def __init__(
        self,
        redis_url: str,
        queue_name: str = "graphcoder:jobs",
    ) -> None:
        self._redis = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=None,
            health_check_interval=30,
        )
        self._queue_name = queue_name

    async def enqueue(self, job_id: str) -> None:
        await self._redis.rpush(self._queue_name, job_id)

    async def dequeue(self, timeout_seconds: int) -> str | None:
        result = await self._redis.blpop(
            [self._queue_name],
            timeout=timeout_seconds,
        )

        if result is None:
            return None

        _, job_id = result
        return job_id

    async def close(self) -> None:
        await self._redis.aclose()
