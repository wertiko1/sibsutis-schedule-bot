from datetime import datetime

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from keyboards.schedule import now_keyboard
from models import User
from services.formatter import format_now

from . import NOVO_TZ, service

router = Router()


@router.message(Command("now"))
async def cmd_now(message: Message, user: User) -> None:
    now_dt = datetime.now(NOVO_TZ)
    schedule = await service.get_month(user.group_id, now_dt.month)
    day_schedule = schedule.days[now_dt.day - 1]
    text, slot_idx, total = format_now(day_schedule, user.group_name, now_dt.time())
    await message.answer(text, reply_markup=now_keyboard(slot_idx, total))


@router.callback_query(F.data == "schedule_now")
async def cb_now(call: CallbackQuery, user: User) -> None:
    now_dt = datetime.now(NOVO_TZ)
    schedule = await service.get_month(user.group_id, now_dt.month)
    day_schedule = schedule.days[now_dt.day - 1]
    text, slot_idx, total = format_now(day_schedule, user.group_name, now_dt.time())
    try:
        await call.message.edit_text(text, reply_markup=now_keyboard(slot_idx, total))
    except TelegramBadRequest:
        pass
    await call.answer()


@router.callback_query(F.data.regexp(r"^now_slot_\d+$"))
async def cb_now_slot(call: CallbackQuery, user: User) -> None:
    idx = int(call.data.split("_")[2])
    now_dt = datetime.now(NOVO_TZ)
    schedule = await service.get_month(user.group_id, now_dt.month)
    day_schedule = schedule.days[now_dt.day - 1]
    text, slot_idx, total = format_now(day_schedule, user.group_name, now_dt.time(), focus_slot=idx)
    await call.message.edit_text(text, reply_markup=now_keyboard(slot_idx, total))
    await call.answer()
