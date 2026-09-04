from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from texts import buttons

PAGE_SIZE = 24


def group_results_keyboard(
    groups: list[dict[str, str]],
    page: int = 0,
) -> InlineKeyboardMarkup:
    total = len(groups)
    start = page * PAGE_SIZE
    page_groups = groups[start : start + PAGE_SIZE]

    builder = InlineKeyboardBuilder()
    for g in page_groups:
        builder.add(InlineKeyboardButton(
            text=g["text"],
            callback_data=f"grp_{g['id']}",
        ))
    cols = 3 if len(page_groups) > 6 else 2 if len(page_groups) > 3 else 1
    builder.adjust(cols)

    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    if total_pages > 1:
        nav: list[InlineKeyboardButton] = []
        if page > 0:
            nav.append(InlineKeyboardButton(text=buttons.BTN_PREV, callback_data=f"grp_page_{page - 1}"))
        nav.append(InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="noop"))
        if page < total_pages - 1:
            nav.append(InlineKeyboardButton(text=buttons.BTN_NEXT, callback_data=f"grp_page_{page + 1}"))
        builder.row(*nav)

    builder.row(InlineKeyboardButton(text=buttons.BTN_CANCEL, callback_data="cancel_group"))
    return builder.as_markup()


def settings_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=buttons.BTN_CHANGE_GROUP, callback_data="change_group"))
    builder.row(InlineKeyboardButton(text=buttons.BTN_MENU, callback_data="back_main"))
    return builder.as_markup()


def onboarding_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=buttons.BTN_SELECT_GROUP, callback_data="change_group"))
    return builder.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=buttons.BTN_CANCEL, callback_data="cancel_group"))
    return builder.as_markup()
