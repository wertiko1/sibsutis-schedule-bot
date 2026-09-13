from datetime import timedelta

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from keyboards.group import onboarding_keyboard
from keyboards.schedule import main_menu
from models import User
from services.formatter import day_button_label
from texts import common, messages
from .deps import service, today

router = Router()


async def _build_main_menu(group: str):
    today_ = today()
    tomorrow = today_ + timedelta(days=1)

    sch_today = await service.get_month(group, today_.month)
    day_today = sch_today.days[today_.day - 1]

    if tomorrow.month == today_.month:
        sch_tomorrow = sch_today
    else:
        sch_tomorrow = await service.get_month(group, tomorrow.month)
    day_tomorrow = sch_tomorrow.days[tomorrow.day - 1]

    today_label = day_button_label(day_today, common.TODAY)
    tomorrow_label = day_button_label(day_tomorrow, common.TOMORROW)

    return main_menu(today_label, tomorrow_label)


@router.callback_query(F.data == "back_main")
async def back_to_main(call: CallbackQuery, user: User) -> None:
    if not user.group_id:
        await call.message.edit_text(messages.ONBOARDING, reply_markup=onboarding_keyboard())
        await call.answer()
        return
    kb = await _build_main_menu(user.group_id)
    await call.message.edit_text(messages.WELCOME, reply_markup=kb)
    await call.answer()


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(messages.HELP)


@router.callback_query(F.data == "noop")
async def noop(call: CallbackQuery) -> None:
    await call.answer()
