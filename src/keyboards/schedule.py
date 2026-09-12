import calendar

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from texts import buttons, common


def main_menu(today_label: str, tomorrow_label: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=buttons.BTN_NOW, callback_data="schedule_now"))
    builder.row(InlineKeyboardButton(text=f"📅  {today_label}", callback_data="schedule_today"))
    builder.row(InlineKeyboardButton(text=f"📆  {tomorrow_label}", callback_data="schedule_tomorrow"))
    builder.row(InlineKeyboardButton(text=buttons.BTN_WEEK, callback_data="schedule_week"))
    builder.row(InlineKeyboardButton(text=buttons.BTN_MONTH_SELECT, callback_data="schedule_months"))
    return builder.as_markup()


def months_menu(current_month: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for offset in range(12):
        month_num = (current_month - 1 + offset) % 12 + 1
        label = common.MONTH_NAMES[month_num - 1]
        if month_num == current_month:
            label = f"{buttons.MONTH_CURRENT_PREFIX}{label}"
        builder.add(InlineKeyboardButton(text=label, callback_data=f"month_{month_num}"))
    builder.adjust(3)
    builder.row(InlineKeyboardButton(text=buttons.BTN_MENU, callback_data="back_main"))
    return builder.as_markup()


def month_overview_keyboard(
    year: int,
    month: int,
    day_lesson_counts: dict[int, int],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(*[
        InlineKeyboardButton(text=wd, callback_data="noop")
        for wd in common.WEEKDAY_HEADERS
    ])

    cal = calendar.monthcalendar(year, month)
    for week in cal:
        row: list[InlineKeyboardButton] = []
        for day_num in week:
            if day_num == 0:
                row.append(InlineKeyboardButton(text=buttons.BTN_CALENDAR_BLANK, callback_data="noop"))
            elif day_lesson_counts.get(day_num, 0) > 0:
                row.append(InlineKeyboardButton(
                    text=str(day_num),
                    callback_data=f"day_{month}_{day_num}",
                ))
            else:
                row.append(InlineKeyboardButton(
                    text=buttons.BTN_CALENDAR_EMPTY,
                    callback_data="noop",
                ))
        builder.row(*row)

    prev_month = 12 if month == 1 else month - 1
    next_month = 1 if month == 12 else month + 1
    builder.row(
        InlineKeyboardButton(text=buttons.BTN_PREV, callback_data=f"month_{prev_month}"),
        InlineKeyboardButton(text=common.MONTH_NAMES[month - 1], callback_data="noop"),
        InlineKeyboardButton(text=buttons.BTN_NEXT, callback_data=f"month_{next_month}"),
    )

    builder.row(InlineKeyboardButton(text=buttons.BTN_ALL_MONTHS, callback_data="schedule_months"))
    builder.row(InlineKeyboardButton(text=buttons.BTN_MENU, callback_data="back_main"))
    return builder.as_markup()


def day_keyboard(day: int, month: int, max_day: int, lesson_labels: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for i, label in enumerate(lesson_labels):
        builder.row(InlineKeyboardButton(text=label, callback_data=f"les_{month}_{day}_{i}"))

    nav: list[InlineKeyboardButton] = []
    if day > 1:
        nav.append(InlineKeyboardButton(text=buttons.BTN_PREV, callback_data=f"day_{month}_{day - 1}"))
    nav.append(InlineKeyboardButton(text=f"{day:02d}.{month:02d}", callback_data="noop"))
    if day < max_day:
        nav.append(InlineKeyboardButton(text=buttons.BTN_NEXT, callback_data=f"day_{month}_{day + 1}"))
    builder.row(*nav)

    builder.row(InlineKeyboardButton(text=buttons.BTN_TO_MONTH, callback_data=f"month_{month}"))
    builder.row(InlineKeyboardButton(text=buttons.BTN_MENU, callback_data="back_main"))
    return builder.as_markup()


def now_keyboard(current_slot: int, total_slots: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    nav: list[InlineKeyboardButton] = []
    if total_slots > 0 and current_slot > 0:
        nav.append(InlineKeyboardButton(text=buttons.BTN_PREV, callback_data=f"now_slot_{current_slot - 1}"))
    nav.append(InlineKeyboardButton(text=buttons.BTN_REFRESH, callback_data="schedule_now"))
    if total_slots > 0 and current_slot < total_slots - 1:
        nav.append(InlineKeyboardButton(text=buttons.BTN_NEXT, callback_data=f"now_slot_{current_slot + 1}"))
    builder.row(*nav)

    builder.row(InlineKeyboardButton(text=buttons.BTN_MENU, callback_data="back_main"))
    return builder.as_markup()


def lesson_detail_keyboard(day: int, month: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=buttons.BTN_BACK_TO_DAY, callback_data=f"day_{month}_{day}"))
    builder.row(InlineKeyboardButton(text=buttons.BTN_MENU, callback_data="back_main"))
    return builder.as_markup()


def week_keyboard(
    day_labels: list[str],
    day_callbacks: list[str],
    prev_cb: str,
    next_cb: str,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for label, cb in zip(day_labels, day_callbacks):
        builder.row(InlineKeyboardButton(text=label, callback_data=cb))

    builder.row(
        InlineKeyboardButton(text=buttons.BTN_PREV, callback_data=prev_cb),
        InlineKeyboardButton(text=buttons.BTN_NEXT, callback_data=next_cb),
    )
    builder.row(InlineKeyboardButton(text=buttons.BTN_MENU, callback_data="back_main"))
    return builder.as_markup()


def back_to_main() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=buttons.BTN_MENU, callback_data="back_main"))
    return builder.as_markup()
