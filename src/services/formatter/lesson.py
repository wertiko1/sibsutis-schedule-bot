from sibsutis_schedule import DaySchedule, Lesson

from texts import common, messages

from ._helpers import shorten


def format_lesson(lesson: Lesson) -> str:
    emoji = common.LESSON_TYPE_EMOJI.get(lesson.lesson_type, common.LESSON_TYPE_EMOJI_DEFAULT)
    lesson_type = common.LESSON_TYPE_SHORT.get(lesson.lesson_type, lesson.lesson_type)
    subgroup = f" <i>({lesson.subgroup})</i>" if lesson.subgroup else ""

    line1 = messages.LESSON_LINE.format(
        emoji=emoji, t_start=lesson.time_begin, t_end=lesson.time_end,
        name=lesson.discipline, subgroup=subgroup,
    )

    lines: list[str] = [line1, f"📝 <i>{lesson_type}</i>"]
    teachers = ", ".join(t for t in lesson.teachers if t)
    if teachers:
        if len(teachers) > 35:
            teachers = teachers[:32] + "..."
        lines.append(messages.LESSON_DETAIL_TEACHER.format(teachers=teachers))
    if lesson.classroom:
        lines.append(messages.LESSON_DETAIL_ROOM.format(room=lesson.classroom))

    return "\n".join(lines)


_BTN_MAX_LEN = 35


def lesson_button_label(lesson: Lesson) -> str:
    emoji = common.LESSON_TYPE_EMOJI.get(lesson.lesson_type, common.LESSON_TYPE_EMOJI_DEFAULT)
    prefix = f"{lesson.time_begin} {emoji} "
    suffix = ""
    if lesson.classroom:
        suffix += f" · {lesson.classroom}"
    if lesson.subgroup:
        suffix += f" ({lesson.subgroup})"
    name = shorten(lesson.discipline, _BTN_MAX_LEN - len(prefix) - len(suffix))
    return f"{prefix}{name}{suffix}"


def format_slot(slot: list[Lesson]) -> str:
    if len(slot) == 1:
        return format_lesson(slot[0])

    first = slot[0]
    all_same = all(
        l.discipline == first.discipline
        and l.lesson_type == first.lesson_type
        and l.teachers == first.teachers
        and l.classroom == first.classroom
        for l in slot[1:]
    )

    if all_same:
        subs = ", ".join(l.subgroup for l in slot if l.subgroup)
        subgroup = f" <i>({subs})</i>" if subs else ""
        emoji = common.LESSON_TYPE_EMOJI.get(first.lesson_type, common.LESSON_TYPE_EMOJI_DEFAULT)
        lesson_type = common.LESSON_TYPE_SHORT.get(first.lesson_type, first.lesson_type)

        line1 = messages.LESSON_LINE.format(
            emoji=emoji, t_start=first.time_begin, t_end=first.time_end,
            name=first.discipline, subgroup=subgroup,
        )
        lines: list[str] = [line1, f"📝 <i>{lesson_type}</i>"]
        teachers = ", ".join(t for t in first.teachers if t)
        if teachers:
            if len(teachers) > 35:
                teachers = teachers[:32] + "..."
            lines.append(messages.LESSON_DETAIL_TEACHER.format(teachers=teachers))
        if first.classroom:
            lines.append(messages.LESSON_DETAIL_ROOM.format(room=first.classroom))
        return "\n".join(lines)

    return "\n".join(format_lesson(l) for l in slot)


def slot_button_label(slot: list[Lesson]) -> str:
    if len(slot) == 1:
        return lesson_button_label(slot[0])

    first = slot[0]
    disciplines = set(l.discipline for l in slot)
    emoji = common.LESSON_TYPE_EMOJI.get(first.lesson_type, common.LESSON_TYPE_EMOJI_DEFAULT)

    if len(disciplines) == 1:
        prefix = f"{first.time_begin} {emoji} "
        rooms = sorted(set(l.classroom for l in slot if l.classroom))
        suffix = f" · {', '.join(rooms)}" if rooms else ""
        name = shorten(first.discipline, _BTN_MAX_LEN - len(prefix) - len(suffix))
        return f"{prefix}{name}{suffix}"

    prefix = f"{first.time_begin} {emoji} "
    avail = _BTN_MAX_LEN - len(prefix) - (len(slot) - 1) * 3
    per_name = max(avail // len(slot), 6)
    names = [shorten(l.discipline, per_name) for l in slot]
    return f"{prefix}{' / '.join(names)}"


def format_lesson_detail(lesson: Lesson, day: DaySchedule, group: str) -> str:
    emoji = common.LESSON_TYPE_EMOJI.get(lesson.lesson_type, common.LESSON_TYPE_EMOJI_DEFAULT)
    lesson_type = common.LESSON_TYPE_SHORT.get(lesson.lesson_type, lesson.lesson_type)
    wd = common.WEEKDAYS_SHORT.get(day.weekday, day.weekday)

    parts = [
        messages.LESSON_DETAIL_TITLE.format(emoji=emoji, name=lesson.discipline),
        "",
        messages.LESSON_DETAIL_TIME.format(t_start=lesson.time_begin, t_end=lesson.time_end),
        f"📝 <i>{lesson_type}</i>",
    ]

    if lesson.subgroup:
        parts.append(messages.LESSON_DETAIL_SUBGROUP.format(subgroup=lesson.subgroup))

    teachers = ", ".join(t for t in lesson.teachers if t)
    if teachers:
        parts.append(messages.LESSON_DETAIL_TEACHER.format(teachers=teachers))

    if lesson.classroom:
        parts.append(messages.LESSON_DETAIL_ROOM.format(room=lesson.classroom))

    parts.append("")
    parts.append(messages.LESSON_DETAIL_FOOTER.format(
        day=day.day, month=day.month, year=day.year, wd=wd, group=group,
    ))

    return "\n".join(parts)


def format_slot_detail(slot: list[Lesson], day: DaySchedule, group: str) -> str:
    if len(slot) == 1:
        return format_lesson_detail(slot[0], day, group)

    wd = common.WEEKDAYS_SHORT.get(day.weekday, day.weekday)
    parts: list[str] = [
        f"🕐 <b>{slot[0].time_begin} – {slot[0].time_end}</b>",
        "",
    ]

    for lesson in slot:
        emoji = common.LESSON_TYPE_EMOJI.get(lesson.lesson_type, common.LESSON_TYPE_EMOJI_DEFAULT)
        lesson_type = common.LESSON_TYPE_SHORT.get(lesson.lesson_type, lesson.lesson_type)
        sub = f" ({lesson.subgroup})" if lesson.subgroup else ""

        parts.append(f"{emoji} <b>{lesson.discipline}</b>{sub}")
        parts.append(f"📝 <i>{lesson_type}</i>")

        teachers = ", ".join(t for t in lesson.teachers if t)
        if teachers:
            parts.append(messages.LESSON_DETAIL_TEACHER.format(teachers=teachers))
        if lesson.classroom:
            parts.append(messages.LESSON_DETAIL_ROOM.format(room=lesson.classroom))
        parts.append("")

    parts.append(messages.LESSON_DETAIL_FOOTER.format(
        day=day.day, month=day.month, year=day.year, wd=wd, group=group,
    ))

    return "\n".join(parts)
