from datetime import timedelta, date

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from keyboards.schedule import day_keyboard, lesson_detail_keyboard
from models import User
from services.formatter import format_day_header, format_slot_detail, slot_button_label
from services.formatter._helpers import group_lessons

from . import service, today
router = Router()


def _slot_labels(day_schedule) -> list[str]:
    slots = group_lessons(day_schedule.lessons)
    return [slot_button_label(slot) for slot in slots]


async def _get_day(group: str, d: date):
    schedule = await service.get_month(group, d.month)
    day_schedule = schedule.days[d.day - 1]
    max_day = len(schedule.days)
    return day_schedule, max_day


async def _send_day(target: Message, group: str, group_name: str, d: date) -> None:
    day_schedule, max_day = await _get_day(group, d)
    text = format_day_header(day_schedule, group_name)
    labels = _slot_labels(day_schedule)
    await target.answer(text, reply_markup=day_keyboard(d.day, d.month, max_day, labels))


async def _edit_day(message: Message, group: str, group_name: str, d: date) -> None:
    day_schedule, max_day = await _get_day(group, d)
    text = format_day_header(day_schedule, group_name)
    labels = _slot_labels(day_schedule)
    await message.edit_text(text, reply_markup=day_keyboard(d.day, d.month, max_day, labels))


@router.message(Command("today"))
async def cmd_today(message: Message, user: User) -> None:
    await _send_day(message, user.group_id, user.group_name, today())


@router.message(Command("tomorrow"))
async def cmd_tomorrow(message: Message, user: User) -> None:
    await _send_day(message, user.group_id, user.group_name, today() + timedelta(days=1))


@router.callback_query(F.data == "schedule_today")
async def cb_today(call: CallbackQuery, user: User) -> None:
    await _edit_day(call.message, user.group_id, user.group_name, today())
    await call.answer()


@router.callback_query(F.data == "schedule_tomorrow")
async def cb_tomorrow(call: CallbackQuery, user: User) -> None:
    await _edit_day(call.message, user.group_id, user.group_name, today() + timedelta(days=1))
    await call.answer()


@router.callback_query(F.data.regexp(r"^day_\d+_\d+$"))
async def cb_day(call: CallbackQuery, user: User) -> None:
    _, month_str, day_str = call.data.split("_")
    month = int(month_str)
    day = int(day_str)

    schedule = await service.get_month(user.group_id, month)
    day_schedule = schedule.days[day - 1]
    text = format_day_header(day_schedule, user.group_name)
    labels = _slot_labels(day_schedule)
    max_day = len(schedule.days)

    await call.message.edit_text(text, reply_markup=day_keyboard(day, month, max_day, labels))
    await call.answer()


@router.callback_query(F.data.regexp(r"^les_\d+_\d+_\d+$"))
async def cb_lesson(call: CallbackQuery, user: User) -> None:
    _, month_str, day_str, idx_str = call.data.split("_")
    month = int(month_str)
    day = int(day_str)
    idx = int(idx_str)

    schedule = await service.get_month(user.group_id, month)
    day_schedule = schedule.days[day - 1]
    slots = group_lessons(day_schedule.lessons)
    slot = slots[idx]
    text = format_slot_detail(slot, day_schedule, user.group_name)

    await call.message.edit_text(text, reply_markup=lesson_detail_keyboard(day, month))
    await call.answer()
