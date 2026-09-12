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

    async def get_month(self, group: str, month: int) -> MonthSchedule:
        key = (group, month)
        if key in self._cache:
            schedule, cached_at = self._cache[key]
            if monotonic() - cached_at < self._ttl:
                logger.debug("Cache hit for group={}, month={}", group, month)
                return schedule
            del self._cache[key]
            logger.debug("Cache expired for group={}, month={}", group, month)

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
        await self._client.close()
