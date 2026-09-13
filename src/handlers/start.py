from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.group import onboarding_keyboard
from models import User
from texts import messages
from .common import _build_main_menu

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, user: User) -> None:
    if not user.group_id:
        await message.answer(messages.ONBOARDING, reply_markup=onboarding_keyboard())
        return
    kb = await _build_main_menu(user.group_id)
    await message.answer(messages.WELCOME, reply_markup=kb)
