import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sibsutis_schedule.models import DaySchedule, Lesson
from services.schedule_diff import diff_day, diff_days


def _lesson(**kwargs) -> Lesson:
    defaults = {
        "time_begin": "09:00",
        "time_end": "10:30",
        "discipline": "Математика",
        "lesson_type": "Лекционные занятия",
        "teachers": ["Иванов И.И."],
        "classroom": "301",
        "subgroup": None,
        "weekday": "Понедельник",
    }
    defaults.update(kwargs)
    return Lesson(**defaults)


def _day(day: int = 1, month: int = 9, lessons: list[Lesson] | None = None) -> DaySchedule:
    return DaySchedule(
        day=day, month=month, year=2026,
        weekday="Понедельник",
        lessons=lessons or [],
    )


class TestDiffDay:
    def test_no_changes(self):
        lessons = [_lesson()]
        old = _day(lessons=lessons)
        new = _day(lessons=lessons)
        assert diff_day(old, new) is None

    def test_added_lesson(self):
        old = _day(lessons=[])
        new = _day(lessons=[_lesson()])
        diff = diff_day(old, new)
        assert diff is not None
        assert len(diff.added) == 1
        assert len(diff.removed) == 0
        assert len(diff.changed) == 0
        assert diff.added[0].discipline == "Математика"

    def test_removed_lesson(self):
        old = _day(lessons=[_lesson()])
        new = _day(lessons=[])
        diff = diff_day(old, new)
        assert diff is not None
        assert len(diff.added) == 0
        assert len(diff.removed) == 1
        assert diff.removed[0].discipline == "Математика"

    def test_changed_classroom(self):
        old = _day(lessons=[_lesson(classroom="301")])
        new = _day(lessons=[_lesson(classroom="405")])
        diff = diff_day(old, new)
        assert diff is not None
        assert len(diff.changed) == 1
        old_l, new_l = diff.changed[0]
        assert old_l.classroom == "301"
        assert new_l.classroom == "405"

    def test_changed_teacher(self):
        old = _day(lessons=[_lesson(teachers=["Иванов И.И."])])
        new = _day(lessons=[_lesson(teachers=["Петров П.П."])])
        diff = diff_day(old, new)
        assert diff is not None
        assert len(diff.changed) == 1

    def test_changed_discipline(self):
        old = _day(lessons=[_lesson(discipline="Математика")])
        new = _day(lessons=[_lesson(discipline="Физика")])
        diff = diff_day(old, new)
        assert diff is not None
        assert len(diff.changed) == 1

    def test_replaced_lesson_different_time(self):
        old = _day(lessons=[_lesson(time_begin="09:00", time_end="10:30")])
        new = _day(lessons=[_lesson(time_begin="11:00", time_end="12:30")])
        diff = diff_day(old, new)
        assert diff is not None
        assert len(diff.removed) == 1
        assert len(diff.added) == 1

    def test_multiple_changes(self):
        old = _day(lessons=[
            _lesson(time_begin="09:00", time_end="10:30", discipline="Математика"),
            _lesson(time_begin="11:00", time_end="12:30", discipline="Физика"),
            _lesson(time_begin="13:00", time_end="14:30", discipline="Химия"),
        ])
        new = _day(lessons=[
            _lesson(time_begin="09:00", time_end="10:30", discipline="Математика"),
            _lesson(time_begin="11:00", time_end="12:30", discipline="Физика", classroom="999"),
            # Химия removed, Биология added
            _lesson(time_begin="15:00", time_end="16:30", discipline="Биология"),
        ])
        diff = diff_day(old, new)
        assert diff is not None
        assert len(diff.added) == 1
        assert diff.added[0].discipline == "Биология"
        assert len(diff.removed) == 1
        assert diff.removed[0].discipline == "Химия"
        assert len(diff.changed) == 1
        assert diff.changed[0][1].classroom == "999"

    def test_subgroup_as_key(self):
        old = _day(lessons=[
            _lesson(subgroup="1", discipline="Лаба А"),
            _lesson(subgroup="2", discipline="Лаба Б"),
        ])
        new = _day(lessons=[
            _lesson(subgroup="1", discipline="Лаба А"),
            _lesson(subgroup="2", discipline="Лаба В"),  # changed
        ])
        diff = diff_day(old, new)
        assert diff is not None
        assert len(diff.changed) == 1
        assert diff.changed[0][1].discipline == "Лаба В"


class TestDiffDays:
    def test_no_changes(self):
        days = [_day(day=1, lessons=[_lesson()]), _day(day=2, lessons=[])]
        assert diff_days(days, days) == []

    def test_change_on_one_day(self):
        old = [_day(day=1, lessons=[_lesson(classroom="301")]), _day(day=2)]
        new = [_day(day=1, lessons=[_lesson(classroom="405")]), _day(day=2)]
        diffs = diff_days(old, new)
        assert len(diffs) == 1
        assert diffs[0].day.day == 1

    def test_new_day_with_lessons(self):
        old = [_day(day=1)]
        new = [_day(day=1), _day(day=2, lessons=[_lesson()])]
        diffs = diff_days(old, new)
        assert len(diffs) == 1
        assert diffs[0].day.day == 2
        assert len(diffs[0].added) == 1

    def test_new_day_without_lessons_ignored(self):
        old = [_day(day=1)]
        new = [_day(day=1), _day(day=2, lessons=[])]
        diffs = diff_days(old, new)
        assert len(diffs) == 0

    def test_changes_across_months(self):
        old = [
            _day(day=30, month=9, lessons=[_lesson(discipline="Математика")]),
            _day(day=1, month=10, lessons=[_lesson(discipline="Физика")]),
        ]
        new = [
            _day(day=30, month=9, lessons=[_lesson(discipline="Математика")]),
            _day(day=1, month=10, lessons=[_lesson(discipline="Химия")]),
        ]
        diffs = diff_days(old, new)
        assert len(diffs) == 1
        assert diffs[0].day.month == 10
