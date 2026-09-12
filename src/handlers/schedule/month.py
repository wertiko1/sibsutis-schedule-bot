from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards.schedule import month_overview_keyboard, months_menu
from models import User
from services.formatter import format_month_overview
from services.formatter._helpers import group_lessons
from texts import messages
from . import service, today

router = Router()


@router.callback_query(F.data == "schedule_months")
async def cb_months(call: CallbackQuery) -> None:
    current_month = today().month
    await call.message.edit_text(
        messages.PICK_MONTH,
        reply_markup=months_menu(current_month),
    )
    await call.answer()


@router.callback_query(F.data.startswith("month_"))
async def cb_month(call: CallbackQuery, user: User) -> None:
    month = int(call.data.split("_")[1])
    schedule = await service.get_month(user.group_id, month)
    text = format_month_overview(schedule, user.group_name)

    day_counts = {
        d.day: len(group_lessons(d.lessons))
        for d in schedule.days
        if d.lessons
    }
    kb = month_overview_keyboard(schedule.year, month, day_counts)

    await call.message.edit_text(text, reply_markup=kb)
    await call.answer()
