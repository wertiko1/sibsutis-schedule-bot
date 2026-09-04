from sibsutis_schedule import MonthSchedule

from texts import common, messages

from ._helpers import group_lessons, lesson_word


def format_month_overview(schedule: MonthSchedule, group: str) -> str:
    month_name = common.MONTH_NAMES[schedule.month - 1]

    total_days = sum(1 for d in schedule.days if d.lessons)
    total_lessons = sum(len(group_lessons(d.lessons)) for d in schedule.days if d.lessons)

    header = messages.MONTH_HEADER.format(name=month_name, year=schedule.year, group=group)
    summary = messages.MONTH_SUMMARY.format(
        days=total_days, lessons=total_lessons, word=lesson_word(total_lessons),
    )

    return f"{header}\n{summary}\n\n{messages.PICK_DAY}"
