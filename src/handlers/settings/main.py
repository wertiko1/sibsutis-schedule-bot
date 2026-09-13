from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.group import settings_keyboard
from models import User
from texts import common, messages

router = Router()


@router.message(Command("settings"))
async def cmd_settings(message: Message, user: User) -> None:
    text = messages.GROUP_CURRENT.format(
        group=user.group_name or "—",
        notify_status=common.NOTIFY_STATUS[user.notify],
    )
    await message.answer(text, reply_markup=settings_keyboard(user.notify))
