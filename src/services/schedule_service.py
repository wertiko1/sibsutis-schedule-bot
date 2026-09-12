import asyncio
from time import monotonic

from loguru import logger

from sibsutis_schedule import AsyncSibsutisClient, MonthSchedule

DEFAULT_TTL_SECONDS = 30 * 60


class ScheduleService:
    def __init__(
            self,
            login: str,
            password: str,
            proxy_url: str | None = None,
            cache_ttl: int = DEFAULT_TTL_SECONDS,
    ) -> None:
        self._client = AsyncSibsutisClient(login, password, proxy_url=proxy_url)
        self._cache: dict[tuple[str, int], tuple[MonthSchedule, float]] = {}
        self._ttl = cache_ttl
        self._refresh_task: asyncio.Task | None = None

    def start_background_refresh(self) -> None:
        if self._refresh_task is None:
            self._refresh_task = asyncio.create_task(self._refresh_loop())
            logger.info("Background cache refresh started (TTL={}s)", self._ttl)

    async def _refresh_loop(self) -> None:
        while True:
            await asyncio.sleep(self._ttl)
            await self._refresh_stale()

    async def _refresh_stale(self) -> None:
        now = monotonic()
        stale_keys = [
            key for key, (_, cached_at) in self._cache.items()
            if now - cached_at >= self._ttl
        ]
        for group, month in stale_keys:
            try:
                logger.info("Background refresh group={}, month={}", group, month)
                schedule = await self._client.get_schedule(group, month=month)
                self._cache[(group, month)] = (schedule, monotonic())
            except Exception:
                logger.warning("Background refresh failed for group={}, month={}", group, month)

    async def get_month(self, group: str, month: int) -> MonthSchedule:
        key = (group, month)
        if key in self._cache:
            schedule, _ = self._cache[key]
            logger.debug("Cache hit for group={}, month={}", group, month)
            return schedule

        logger.info("Fetching schedule for group={}, month={}", group, month)
        schedule = await self._client.get_schedule(group, month=month)
        self._cache[key] = (schedule, monotonic())
        return schedule

    async def search_groups(self, query: str) -> list[dict[str, str]]:
        return await self._client.search_groups(query)

    def invalidate(self) -> None:
        self._cache.clear()
        logger.info("Schedule cache invalidated")

    async def close(self) -> None:
        if self._refresh_task is not None:
            self._refresh_task.cancel()
            self._refresh_task = None
        await self._client.close()
