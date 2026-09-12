from datetime import time

from sibsutis_schedule import DaySchedule
from texts import common, messages
from ._helpers import format_minutes, group_lessons, lesson_word, minutes_between, parse_time
from .lesson import format_slot


def format_now(
        day: DaySchedule,
        group: str,
        now: time,
        focus_slot: int | None = None,
) -> tuple[str, int, int]:
    wd = common.WEEKDAYS_SHORT.get(day.weekday, day.weekday)
    header = messages.NOW_HEADER.format(day=day.day, month=day.month, wd=wd, group=group)

    if not day.lessons:
        return f"{header}\n\n{messages.NOW_NO_LESSONS}", -1, 0

    slots = group_lessons(day.lessons)
    total = len(slots)

    if focus_slot is not None:
        slot = slots[focus_slot]
        begin = parse_time(slot[0].time_begin)
        end = parse_time(slot[0].time_end)

        parts: list[str] = [header, ""]
        parts.append(messages.NOW_FOCUSED.format(i=focus_slot + 1, total=total))
        parts.append(format_slot(slot))

        if now < begin:
            wait = minutes_between(now, begin)
            parts.append(f"\n{messages.NOW_FOCUSED_STARTS_IN.format(time=format_minutes(wait))}")
        elif begin <= now < end:
            left = minutes_between(now, end)
            parts.append(f"\n{messages.NOW_FOCUSED_ONGOING.format(time=format_minutes(left))}")
        else:
            parts.append(f"\n{messages.NOW_FOCUSED_FINISHED}")

        return "\n".join(parts), focus_slot, total

    for i, slot in enumerate(slots):
        begin = parse_time(slot[0].time_begin)
        end = parse_time(slot[0].time_end)

        if now < begin:
            wait = minutes_between(now, begin)
            parts = [header, ""]
            if i == 0:
                parts.append(messages.NOW_NOT_STARTED)
            else:
                parts.append(messages.NOW_BREAK)
            parts.append(messages.NOW_UNTIL_NEXT.format(time=format_minutes(wait)))
            parts.append("")
            parts.append(messages.NOW_NEXT)
            parts.append(format_slot(slot))
            remaining = total - i - 1
            if remaining > 0:
                parts.append(f"\n{messages.NOW_REMAINING.format(n=remaining, word=lesson_word(remaining))}")
            nav_total = 0 if i == 0 else total
            return "\n".join(parts), i, nav_total

        if begin <= now < end:
            left = minutes_between(now, end)
            parts = [header, ""]
            parts.append(messages.NOW_CURRENT.format(i=i + 1, total=total))
            parts.append(format_slot(slot))
            parts.append(f"\n{messages.NOW_TIME_LEFT.format(time=format_minutes(left))}")

            if i + 1 < total:
                nxt_slot = slots[i + 1]
                nxt_begin = parse_time(nxt_slot[0].time_begin)
                gap = minutes_between(end, nxt_begin)
                parts.append("")
                parts.append(messages.NOW_UPCOMING.format(gap=format_minutes(gap)))
                parts.append(format_slot(nxt_slot))
            else:
                parts.append(f"\n{messages.NOW_LAST}")

            return "\n".join(parts), i, total

    return f"{header}\n\n{messages.NOW_DONE}", total - 1, 0
