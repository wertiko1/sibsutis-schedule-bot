import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sibsutis_schedule.extractors import parse_lessons


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
