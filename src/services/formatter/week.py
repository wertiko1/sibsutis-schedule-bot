from sibsutis_schedule import DaySchedule

from texts import common, messages

from ._helpers import group_lessons, lesson_word


def _format_week_day(day: DaySchedule) -> str:
    wd = common.WEEKDAYS_SHORT.get(day.weekday, day.weekday)
    header = messages.WEEK_DAY.format(wd=wd, day=day.day, month=day.month)

    if not day.lessons:
        return f"{header}{messages.WEEK_NO_LESSONS}"

    slots = group_lessons(day.lessons)
    lines = [header]
    for slot in slots:
        lesson = slot[0]
        emoji = common.LESSON_TYPE_EMOJI.get(lesson.lesson_type, common.LESSON_TYPE_EMOJI_DEFAULT)
        name = lesson.discipline
        if len(slot) > 1:
            disciplines = set(l.discipline for l in slot)
            if len(disciplines) > 1:
                name = " / ".join(l.discipline for l in slot)
        sub = ""
        if len(slot) == 1 and lesson.subgroup:
            sub = f" <i>({lesson.subgroup})</i>"
        lines.append(f"  {emoji} {lesson.time_begin}–{lesson.time_end}  {name}{sub}")

    return "\n".join(lines)


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

    body = "\n".join(_format_week_day(d) for d in days)

    return f"{header}\n{summary}\n{body}"
