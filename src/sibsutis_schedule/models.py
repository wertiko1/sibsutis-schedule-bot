from pydantic import BaseModel


class Lesson(BaseModel):
    time_begin: str
    time_end: str
    discipline: str
    lesson_type: str
    teachers: list[str]
    classroom: str
    subgroup: str | None = None
    weekday: str


class DaySchedule(BaseModel):
    day: int
    month: int
    year: int
    weekday: str
    lessons: list[Lesson]


class MonthSchedule(BaseModel):
    year: int
    month: int
    group: str
    days: list[DaySchedule]
