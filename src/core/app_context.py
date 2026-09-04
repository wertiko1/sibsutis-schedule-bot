from dataclasses import dataclass

from aiogram import Bot, Dispatcher

from db import PostgresClient


@dataclass
class AppContext:
    bot: Bot
    dispatcher: Dispatcher
    db: PostgresClient

    async def shutdown(self) -> None:
        await self.db.shutdown()
        await self.dispatcher.storage.close()
