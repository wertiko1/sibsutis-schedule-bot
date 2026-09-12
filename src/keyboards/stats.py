from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from texts import buttons


def stats_hub_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=buttons.BTN_STATS_ACTIVITY, callback_data="st_activity"),
        InlineKeyboardButton(text=buttons.BTN_STATS_ACTIONS, callback_data="st_actions"),
        InlineKeyboardButton(text=buttons.BTN_STATS_AUDIENCE, callback_data="st_audience"),
    )
    return builder.as_markup()


def stats_back_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=buttons.BTN_STATS_BACK, callback_data="st_hub"))
    return builder.as_markup()
