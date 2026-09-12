from datetime import date, timedelta

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from keyboards.schedule import week_keyboard
from models import User
from services.formatter import format_week
from sibsutis_schedule import DaySchedule

from . import service, today

router = Router()


def _monday_of(d: date) -> date:
    return d - timedelta(days=d.weekday())


async def _get_week_days(group: str, monday: date) -> list[DaySchedule]:
    days: list[DaySchedule] = []
    for offset in range(6):
        d = monday + timedelta(days=offset)
        schedule = await service.get_month(group, d.month)
        days.append(schedule.days[d.day - 1])
    return days


def _week_callback(monday: date, direction: str) -> str:
    offset = timedelta(weeks=-1) if direction == "prev" else timedelta(weeks=1)
    target = monday + offset
    return f"week_{target.month}_{target.day}"


async def _send_week(target: Message, group: str, group_name: str, monday: date) -> None:
    days = await _get_week_days(group, monday)
    text = format_week(days, group_name)
    prev_cb = _week_callback(monday, "prev")
    next_cb = _week_callback(monday, "next")
    await target.answer(text, reply_markup=week_keyboard(prev_cb, next_cb))


async def _edit_week(message: Message, group: str, group_name: str, monday: date) -> None:
    days = await _get_week_days(group, monday)
    text = format_week(days, group_name)
    prev_cb = _week_callback(monday, "prev")
    next_cb = _week_callback(monday, "next")
    await message.edit_text(text, reply_markup=week_keyboard(prev_cb, next_cb))


@router.message(Command("week"))
async def cmd_week(message: Message, user: User) -> None:
    monday = _monday_of(today())
    await _send_week(message, user.group_id, user.group_name, monday)


@router.callback_query(F.data == "schedule_week")
async def cb_week(call: CallbackQuery, user: User) -> None:
    monday = _monday_of(today())
    await _edit_week(call.message, user.group_id, user.group_name, monday)
    await call.answer()


@router.callback_query(F.data.regexp(r"^week_\d+_\d+$"))
async def cb_week_nav(call: CallbackQuery, user: User) -> None:
    _, month_str, day_str = call.data.split("_")
    month = int(month_str)
    day = int(day_str)

    schedule = await service.get_month(user.group_id, month)
    year = schedule.year
    monday = date(year, month, day)

    await _edit_week(call.message, user.group_id, user.group_name, monday)
    await call.answer()
