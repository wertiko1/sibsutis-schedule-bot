from dataclasses import dataclass

from sibsutis_schedule import DaySchedule, Lesson


@dataclass
class DayDiff:
    day: DaySchedule
    added: list[Lesson]
    removed: list[Lesson]
    changed: list[tuple[Lesson, Lesson]]
