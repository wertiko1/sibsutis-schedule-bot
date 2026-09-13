from schemas.diff import DayDiff
from texts import common, messages


def format_notification(group_name: str, diffs: list[DayDiff]) -> str:
    lines = [messages.NOTIFY_HEADER.format(group=group_name)]

    for diff in diffs:
        wd = common.WEEKDAYS_SHORT.get(diff.day.weekday, diff.day.weekday)
        lines.append(messages.NOTIFY_DAY.format(day=diff.day.day, month=diff.day.month, wd=wd))

        for lesson in diff.removed:
            lines.append(messages.NOTIFY_REMOVED.format(
                time=f"{lesson.time_begin}–{lesson.time_end}",
                name=lesson.discipline,
            ))
        for lesson in diff.added:
            lines.append(messages.NOTIFY_ADDED.format(
                time=f"{lesson.time_begin}–{lesson.time_end}",
                name=lesson.discipline,
            ))
        for old_l, new_l in diff.changed:
            parts = []
            if old_l.discipline != new_l.discipline:
                parts.append(f"{old_l.discipline} → {new_l.discipline}")
            else:
                parts.append(new_l.discipline)
            if old_l.classroom != new_l.classroom:
                parts.append(f"ауд. {old_l.classroom} → {new_l.classroom}")
            if old_l.teachers != new_l.teachers:
                parts.append("сменился преподаватель")
            lines.append(messages.NOTIFY_CHANGED.format(
                time=f"{new_l.time_begin}–{new_l.time_end}",
                name=" · ".join(parts),
            ))

    return "\n".join(lines)
