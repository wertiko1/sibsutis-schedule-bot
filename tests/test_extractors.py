import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sibsutis_schedule.extractors import parse_lessons
from sibsutis_schedule.models import DaySchedule, Lesson, MonthSchedule


class TestModels:
    def test_lesson_null_classroom(self):
        lesson = Lesson(
            time_begin="08:00", time_end="09:35",
            discipline="Математика", lesson_type="Лекция",
            teachers=["Иванов"], classroom=None, weekday="Понедельник",
        )
        assert lesson.classroom is None

    def test_lesson_null_subgroup(self):
        lesson = Lesson(
            time_begin="08:00", time_end="09:35",
            discipline="Математика", lesson_type="Лекция",
            teachers=["Иванов"], classroom="301", weekday="Понедельник",
        )
        assert lesson.subgroup is None

    def test_lesson_defaults(self):
        lesson = Lesson(
            time_begin="08:00", time_end="09:35",
            discipline="Математика", lesson_type="Лекция",
            teachers=[], weekday="Понедельник",
        )
        assert lesson.classroom is None
        assert lesson.subgroup is None

    def test_day_schedule_empty_lessons(self):
        day = DaySchedule(day=1, month=9, year=2026, weekday="Понедельник", lessons=[])
        assert day.lessons == []

    def test_month_schedule(self):
        day = DaySchedule(day=1, month=9, year=2026, weekday="Понедельник", lessons=[])
        schedule = MonthSchedule(year=2026, month=9, group="test", days=[day])
        assert len(schedule.days) == 1


class TestParseLessons:
    def test_plan_format(self):
        data = {
            "ScheduleCell": [
                {
                    "DateBegin": "0001-01-01T08:00:00",
                    "DateEnd": "0001-01-01T09:35:00",
                    "Subgroup": [
                        {
                            "DISCIPLINE": "Математика",
                            "TYPE_LESSON": "Лекция",
                            "TEACHER": ["Иванов"],
                            "CLASSROOM": "301",
                            "SUBGROUP": None,
                            "WEEK_DAY": "Понедельник",
                        }
                    ],
                }
            ]
        }
        lessons = parse_lessons(data)
        assert len(lessons) == 1
        assert lessons[0].time_begin == "08:00"
        assert lessons[0].time_end == "09:35"
        assert lessons[0].discipline == "Математика"

    def test_fact_format(self):
        data = {
            "ScheduleCell": [
                [],
                [
                    {
                        "DATE_BEGIN": "2026-09-14 09:50:00",
                        "DISCIPLINE": "Информатика",
                        "TYPE_LESSON": "Практика",
                        "TEACHER": ["Петров"],
                        "CLASSROOM": "409",
                        "SUBGROUP": None,
                        "WEEK_DAY": "Понедельник",
                    }
                ],
                [],
            ]
        }
        lessons = parse_lessons(data)
        assert len(lessons) == 1
        assert lessons[0].time_begin == "09:50"
        assert lessons[0].time_end == "11:25"
        assert lessons[0].discipline == "Информатика"

    def test_fact_empty_slots(self):
        data = {"ScheduleCell": [[], [], [], [], [], [], []]}
        lessons = parse_lessons(data)
        assert lessons == []

    def test_fact_multiple_lessons(self):
        data = {
            "ScheduleCell": [
                [],
                [{"DATE_BEGIN": "2026-09-14 09:50:00", "DISCIPLINE": "A",
                  "TYPE_LESSON": "", "TEACHER": [], "CLASSROOM": "", "SUBGROUP": None, "WEEK_DAY": ""}],
                [{"DATE_BEGIN": "2026-09-14 11:40:00", "DISCIPLINE": "B",
                  "TYPE_LESSON": "", "TEACHER": [], "CLASSROOM": "", "SUBGROUP": None, "WEEK_DAY": ""}],
                [{"DATE_BEGIN": "2026-09-14 13:45:00", "DISCIPLINE": "C",
                  "TYPE_LESSON": "", "TEACHER": [], "CLASSROOM": "", "SUBGROUP": None, "WEEK_DAY": ""}],
                [], [], [],
            ]
        }
        lessons = parse_lessons(data)
        assert len(lessons) == 3
        assert lessons[0].discipline == "A"
        assert lessons[1].discipline == "B"
        assert lessons[2].discipline == "C"

    def test_plan_empty_subgroups_skipped(self):
        data = {
            "ScheduleCell": [
                {"DateBegin": "0001-01-01T15:35:00", "DateEnd": "0001-01-01T17:10:00", "Subgroup": []},
            ]
        }
        lessons = parse_lessons(data)
        assert lessons == []

    def test_null_classroom(self):
        data = {
            "ScheduleCell": [
                {
                    "DateBegin": "0001-01-01T08:00:00",
                    "DateEnd": "0001-01-01T09:35:00",
                    "Subgroup": [
                        {
                            "DISCIPLINE": "Физика",
                            "TYPE_LESSON": "Лекция",
                            "TEACHER": ["Иванов"],
                            "CLASSROOM": None,
                            "SUBGROUP": None,
                            "WEEK_DAY": "Понедельник",
                        }
                    ],
                }
            ]
        }
        lessons = parse_lessons(data)
        assert len(lessons) == 1
        assert lessons[0].classroom is None

    def test_missing_classroom_key(self):
        data = {
            "ScheduleCell": [
                {
                    "DateBegin": "0001-01-01T08:00:00",
                    "DateEnd": "0001-01-01T09:35:00",
                    "Subgroup": [
                        {
                            "DISCIPLINE": "Физика",
                            "TYPE_LESSON": "Лекция",
                            "TEACHER": [],
                            "WEEK_DAY": "Понедельник",
                        }
                    ],
                }
            ]
        }
        lessons = parse_lessons(data)
        assert len(lessons) == 1
        assert lessons[0].classroom is None

    def test_fact_null_classroom(self):
        data = {
            "ScheduleCell": [
                [
                    {
                        "DATE_BEGIN": "2026-09-14 08:00:00",
                        "DISCIPLINE": "Физика",
                        "TYPE_LESSON": "Лекция",
                        "TEACHER": [],
                        "CLASSROOM": None,
                        "SUBGROUP": None,
                        "WEEK_DAY": "Понедельник",
                    }
                ],
            ]
        }
        lessons = parse_lessons(data)
        assert len(lessons) == 1
        assert lessons[0].classroom is None
