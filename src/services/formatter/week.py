from sibsutis_schedule import DaySchedule

from texts import messages

from ._helpers import group_lessons, lesson_word


def format_week(days: list[DaySchedule], group: str) -> str:
    first, last = days[0], days[-1]
    header = messages.WEEK_HEADER.format(
        d_start=first.day, m_start=first.month,
        d_end=last.day, m_end=last.month,
        group=group,
    )

    total_lessons = sum(len(group_lessons(d.lessons)) for d in days if d.lessons)
    study_days = sum(1 for d in days if d.lessons)
    summary = f"📊 {study_days} уч. дн. · {total_lessons} {lesson_word(total_lessons)}"

    return f"{header}\n{summary}"
