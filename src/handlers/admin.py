from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import settings
from services.stats_service import get_stats
from .deps import NOVO_TZ

router = Router()


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    if message.from_user.id not in settings.bot.ADMIN_IDS:
        return

    text = await get_stats(datetime.now(NOVO_TZ))
    await message.answer(text)
