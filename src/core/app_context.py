from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from aiogram import Bot, Dispatcher

from db import PostgresClient

if TYPE_CHECKING:
    from services.notification_service import NotificationService


@dataclass
class AppContext:
    bot: Bot
    dispatcher: Dispatcher
    db: PostgresClient
    notifier: NotificationService | None = field(default=None)

    async def shutdown(self) -> None:
        if self.notifier:
            await self.notifier.stop()
        await self.db.shutdown()
        await self.dispatcher.storage.close()
