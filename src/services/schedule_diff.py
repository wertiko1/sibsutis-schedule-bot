from dataclasses import dataclass

from sibsutis_schedule import DaySchedule, Lesson


@dataclass
class DayDiff:
    day: DaySchedule
    added: list[Lesson]
    removed: list[Lesson]
    changed: list[tuple[Lesson, Lesson]]  # (old, new)


def _lesson_key(lesson: Lesson) -> tuple:
    return (lesson.time_begin, lesson.time_end, lesson.subgroup)


def diff_day(old: DaySchedule, new: DaySchedule) -> DayDiff | None:
    old_by_key = {_lesson_key(l): l for l in old.lessons}
    new_by_key = {_lesson_key(l): l for l in new.lessons}

    old_keys = set(old_by_key)
    new_keys = set(new_by_key)

    added = [new_by_key[k] for k in new_keys - old_keys]
    removed = [old_by_key[k] for k in old_keys - new_keys]
    changed = []

    for k in old_keys & new_keys:
        old_l = old_by_key[k]
        new_l = new_by_key[k]
        if old_l != new_l:
            changed.append((old_l, new_l))

    if not added and not removed and not changed:
        return None

    return DayDiff(day=new, added=added, removed=removed, changed=changed)


def diff_days(
        old_days: list[DaySchedule],
        new_days: list[DaySchedule],
) -> list[DayDiff]:
    diffs = []
    old_map = {(d.day, d.month): d for d in old_days}
    for new_day in new_days:
        key = (new_day.day, new_day.month)
        old_day = old_map.get(key)
        if old_day is None:
            if new_day.lessons:
                diffs.append(DayDiff(day=new_day, added=new_day.lessons, removed=[], changed=[]))
            continue
        diff = diff_day(old_day, new_day)
        if diff:
            diffs.append(diff)
    return diffs
