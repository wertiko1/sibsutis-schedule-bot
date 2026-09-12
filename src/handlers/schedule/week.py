from datetime import date, timedelta

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from keyboards.schedule import week_keyboard, week_day_keyboard, week_lesson_detail_keyboard
from models import User
from services.formatter import day_button_label, format_day_header, format_slot_detail, slot_button_label, format_week
from services.formatter._helpers import group_lessons
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


def _nav_callback(monday: date, direction: str) -> str:
    offset = timedelta(weeks=-1) if direction == "prev" else timedelta(weeks=1)
    target = monday + offset
    return f"week_{target.month}_{target.day}"


def _build_day_buttons(days: list[DaySchedule]) -> tuple[list[str], list[str]]:
    labels = []
    callbacks = []
    for day in days:
        prefix = f"{day.day:02d}.{day.month:02d}"
        labels.append(day_button_label(day, prefix))
        callbacks.append(f"wday_{day.month}_{day.day}")
    return labels, callbacks


async def _send_week(target: Message, group: str, group_name: str, monday: date) -> None:
    days = await _get_week_days(group, monday)
    text = format_week(days, group_name)
    labels, callbacks = _build_day_buttons(days)
    kb = week_keyboard(labels, callbacks, _nav_callback(monday, "prev"), _nav_callback(monday, "next"))
    await target.answer(text, reply_markup=kb)


async def _edit_week(message: Message, group: str, group_name: str, monday: date) -> None:
    days = await _get_week_days(group, monday)
    text = format_week(days, group_name)
    labels, callbacks = _build_day_buttons(days)
    kb = week_keyboard(labels, callbacks, _nav_callback(monday, "prev"), _nav_callback(monday, "next"))
    await message.edit_text(text, reply_markup=kb)


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


@router.callback_query(F.data.regexp(r"^wday_\d+_\d+$"))
async def cb_week_day(call: CallbackQuery, user: User) -> None:
    _, month_str, day_str = call.data.split("_")
    month = int(month_str)
    day = int(day_str)

    schedule = await service.get_month(user.group_id, month)
    day_schedule = schedule.days[day - 1]
    text = format_day_header(day_schedule, user.group_name)
    slots = group_lessons(day_schedule.lessons)
    labels = [slot_button_label(slot) for slot in slots]
    max_day = len(schedule.days)

    await call.message.edit_text(text, reply_markup=week_day_keyboard(day, month, max_day, labels))
    await call.answer()


@router.callback_query(F.data.regexp(r"^wles_\d+_\d+_\d+$"))
async def cb_week_lesson(call: CallbackQuery, user: User) -> None:
    _, month_str, day_str, idx_str = call.data.split("_")
    month = int(month_str)
    day = int(day_str)
    idx = int(idx_str)

    schedule = await service.get_month(user.group_id, month)
    day_schedule = schedule.days[day - 1]
    slots = group_lessons(day_schedule.lessons)
    slot = slots[idx]
    text = format_slot_detail(slot, day_schedule, user.group_name)

    await call.message.edit_text(text, reply_markup=week_lesson_detail_keyboard(day, month))
    await call.answer()
