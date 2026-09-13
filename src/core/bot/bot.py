from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from core.app_context import AppContext
from core.loader import RouterLoader
from core.logging import Logger
from core.middleware import AnalyticsMiddleware, UserMiddleware
from db import PostgresClient


async def setup_bot() -> AppContext:
    Logger()
    bot = Bot(
        token=settings.bot.TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )

    dp = Dispatcher(storage=MemoryStorage())

    db = PostgresClient()
    await db.startup()

    dp.message.middleware(AnalyticsMiddleware())
    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(AnalyticsMiddleware())
    dp.callback_query.middleware(UserMiddleware())

    loader = RouterLoader("handlers", dp)
    loader.load()

    from handlers.deps import service
    from services.notification_service import NotificationService

    notifier = NotificationService(bot, service)
    notifier.start()

    await bot.set_my_commands(settings.commands)
    await bot.delete_webhook(drop_pending_updates=True)

    return AppContext(bot=bot, dispatcher=dp, db=db, notifier=notifier)
