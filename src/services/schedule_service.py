from loguru import logger

from sibsutis_schedule import AsyncSibsutisClient, MonthSchedule


class ScheduleService:
    def __init__(self, login: str, password: str, proxy_url: str | None = None) -> None:
        self._client = AsyncSibsutisClient(login, password, proxy_url=proxy_url)
        self._cache: dict[tuple[str, int], MonthSchedule] = {}

    async def get_month(self, group: str, month: int) -> MonthSchedule:
        key = (group, month)
        if key in self._cache:
            logger.debug("Cache hit for group={}, month={}", group, month)
            return self._cache[key]

        logger.info("Fetching schedule for group={}, month={}", group, month)
        schedule = await self._client.get_schedule(group, month=month)
        self._cache[key] = schedule
        return schedule

    async def search_groups(self, query: str) -> list[dict[str, str]]:
        return await self._client.search_groups(query)

    def invalidate(self) -> None:
        self._cache.clear()
        logger.info("Schedule cache invalidated")

    async def close(self) -> None:
        await self._client.close()
