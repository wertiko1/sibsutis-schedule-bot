from loguru import logger
from tortoise import Tortoise

from config import settings


class PostgresClient:
    def __init__(self) -> None:
        self._config = settings.db.get_tortoise_config()

    async def startup(self) -> None:
        await Tortoise.init(config=self._config)
        logger.info("Database connected")

    async def shutdown(self) -> None:
        await Tortoise.close_connections()
        logger.info("Database disconnected")
