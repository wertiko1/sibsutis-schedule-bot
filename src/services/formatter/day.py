from datetime import date

from sibsutis_schedule import DaySchedule
from sibsutis_schedule.week_parity import academic_week_number, academic_week_parity

from texts import common, messages

from ._helpers import group_lessons, lesson_word


def format_day_header(day: DaySchedule, group: str) -> str:
    wd = common.WEEKDAYS_SHORT.get(day.weekday, day.weekday)
    day_date = date(day.year, day.month, day.day)
    header = messages.DAY_HEADER.format(
        day=day.day,
        month=day.month,
        year=day.year,
        wd=wd,
        group=group,
        week_number=academic_week_number(day_date),
        week_parity=academic_week_parity(day_date),
    )

    if not day.lessons:
        return f"{header}\n\n{messages.DAY_NO_LESSONS}"

    slots = group_lessons(day.lessons)
    count = len(slots)
    first = day.lessons[0]
    last = day.lessons[-1]
    summary = messages.DAY_SUMMARY.format(
        count=count, word=lesson_word(count),
        t_start=first.time_begin, t_end=last.time_end,
    )

    return f"{header}\n{summary}"


def day_button_label(day: DaySchedule, prefix: str) -> str:
    wd = common.WEEKDAYS_SHORT.get(day.weekday, day.weekday)

    if not day.lessons:
        return messages.DAY_BTN_OFF.format(prefix=prefix, wd=wd)

    slots = group_lessons(day.lessons)
    count = len(slots)
    first = day.lessons[0]
    last = day.lessons[-1]
    return messages.DAY_BTN.format(
        prefix=prefix, wd=wd, count=count, word=lesson_word(count),
        t_start=first.time_begin, t_end=last.time_end,
    )
