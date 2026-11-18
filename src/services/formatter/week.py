from datetime import date

from sibsutis_schedule import DaySchedule
from sibsutis_schedule.week_parity import academic_week_number, academic_week_parity

from texts import messages

from ._helpers import group_lessons, lesson_word


def format_week(days: list[DaySchedule], group: str) -> str:
    first, last = days[0], days[-1]
    first_date = date(first.year, first.month, first.day)
    header = messages.WEEK_HEADER.format(
        d_start=first.day, m_start=first.month,
        d_end=last.day, m_end=last.month,
        group=group,
        week_number=academic_week_number(first_date),
        week_parity=academic_week_parity(first_date),
    )

    total_lessons = sum(len(group_lessons(d.lessons)) for d in days if d.lessons)
    study_days = sum(1 for d in days if d.lessons)
    summary = f"📊 {study_days} уч. дн. · {total_lessons} {lesson_word(total_lessons)}"

    return f"{header}\n{summary}"
