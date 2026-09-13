import sys
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sibsutis_schedule.models import DaySchedule, Lesson, MonthSchedule
from services.schedule_service import ScheduleService


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


def _month(month: int = 9, lessons: list[Lesson] | None = None) -> MonthSchedule:
    day = DaySchedule(
        day=14, month=month, year=2026,
        weekday="Понедельник",
        lessons=lessons or [],
    )
    return MonthSchedule(year=2026, month=month, group="бв-601", days=[day])


class TestScheduleService:
    @pytest.mark.asyncio
    async def test_get_month_caches(self):
        svc = ScheduleService("login", "pass")
        schedule = _month()
        svc._client = AsyncMock()
        svc._client.get_schedule = AsyncMock(return_value=schedule)

        result1 = await svc.get_month("123", 9)
        result2 = await svc.get_month("123", 9)

        assert result1 is result2
        svc._client.get_schedule.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_month_always_hits_api(self):
        svc = ScheduleService("login", "pass")
        s1 = _month(lessons=[_lesson(classroom="301")])
        s2 = _month(lessons=[_lesson(classroom="405")])
        svc._client = AsyncMock()
        svc._client.get_schedule = AsyncMock(side_effect=[s1, s2])

        result1 = await svc.fetch_month("123", 9)
        result2 = await svc.fetch_month("123", 9)

        assert result1.days[0].lessons[0].classroom == "301"
        assert result2.days[0].lessons[0].classroom == "405"
        assert svc._client.get_schedule.call_count == 2

    @pytest.mark.asyncio
    async def test_fetch_month_updates_cache(self):
        svc = ScheduleService("login", "pass")
        old = _month(lessons=[_lesson(classroom="301")])
        new = _month(lessons=[_lesson(classroom="405")])
        svc._client = AsyncMock()
        svc._client.get_schedule = AsyncMock(side_effect=[old, new])

        await svc.get_month("123", 9)  # cache old
        await svc.fetch_month("123", 9)  # force update
        result = await svc.get_month("123", 9)  # should return new from cache

        assert result.days[0].lessons[0].classroom == "405"
        assert svc._client.get_schedule.call_count == 2  # get_month hit cache

    @pytest.mark.asyncio
    async def test_invalidate_clears_cache(self):
        svc = ScheduleService("login", "pass")
        schedule = _month()
        svc._client = AsyncMock()
        svc._client.get_schedule = AsyncMock(return_value=schedule)

        await svc.get_month("123", 9)
        svc.invalidate()
        await svc.get_month("123", 9)

        assert svc._client.get_schedule.call_count == 2
