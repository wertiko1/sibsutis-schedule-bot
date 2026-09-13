from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from config import settings
from keyboards.stats import stats_hub_keyboard, stats_back_keyboard
from services.formatter.stats import format_hub, format_activity, format_actions, format_audience
from services.stats_service import get_hub_stats, get_activity_stats, get_actions_stats, get_audience_stats
from .deps import NOVO_TZ

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id in settings.bot.ADMIN_IDS


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        return
    now = datetime.now(NOVO_TZ)
    data = await get_hub_stats(now)
    await message.answer(format_hub(data, now), reply_markup=stats_hub_keyboard())


@router.callback_query(F.data == "st_hub")
async def cb_stats_hub(call: CallbackQuery) -> None:
    if not _is_admin(call.from_user.id):
        await call.answer()
        return
    now = datetime.now(NOVO_TZ)
    data = await get_hub_stats(now)
    await call.message.edit_text(format_hub(data, now), reply_markup=stats_hub_keyboard())
    await call.answer()


@router.callback_query(F.data == "st_activity")
async def cb_stats_activity(call: CallbackQuery) -> None:
    if not _is_admin(call.from_user.id):
        await call.answer()
        return
    now = datetime.now(NOVO_TZ)
    data = await get_activity_stats(now)
    await call.message.edit_text(format_activity(data, now), reply_markup=stats_back_keyboard())
    await call.answer()


@router.callback_query(F.data == "st_actions")
async def cb_stats_actions(call: CallbackQuery) -> None:
    if not _is_admin(call.from_user.id):
        await call.answer()
        return
    data = await get_actions_stats()
    await call.message.edit_text(format_actions(data), reply_markup=stats_back_keyboard())
    await call.answer()


@router.callback_query(F.data == "st_audience")
async def cb_stats_audience(call: CallbackQuery) -> None:
    if not _is_admin(call.from_user.id):
        await call.answer()
        return
    now = datetime.now(NOVO_TZ)
    data = await get_audience_stats(now)
    await call.message.edit_text(format_audience(data), reply_markup=stats_back_keyboard())
    await call.answer()
