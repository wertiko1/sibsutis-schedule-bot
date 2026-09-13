import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from datetime import date

from sibsutis_schedule.models import DaySchedule, Lesson, MonthSchedule
from services.notification_service import _fetch_upcoming_days, NotificationService
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


def _full_month(month: int = 9, day_count: int = 30,
                lessons_on: dict[int, list[Lesson]] | None = None) -> MonthSchedule:
    weekdays = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    days = []
    for d in range(1, day_count + 1):
        days.append(DaySchedule(
            day=d, month=month, year=2026,
            weekday=weekdays[d % 7],
            lessons=(lessons_on or {}).get(d, []),
        ))
    return MonthSchedule(year=2026, month=month, group="бв-601", days=days)


class TestFetchUpcomingDays:
    @pytest.mark.asyncio
    async def test_calls_fetch_not_get(self):
        svc = ScheduleService("login", "pass")
        schedule = _full_month(9)
        svc._client = AsyncMock()
        svc._client.get_schedule = AsyncMock(return_value=schedule)

        # pre-populate cache with stale data
        stale = _full_month(9, lessons_on={14: [_lesson(classroom="OLD")]})
        svc._cache[("123", 9)] = stale

        days = await _fetch_upcoming_days(svc, "123", date(2026, 9, 14))

        # fetch_month should have been called, overwriting cache
        svc._client.get_schedule.assert_called_once()
        # returned data should be from API (no lessons), not stale cache
        assert days[0].lessons == []

    @pytest.mark.asyncio
    async def test_fetches_each_month_once(self):
        svc = ScheduleService("login", "pass")
        sep = _full_month(9, day_count=30)
        oct_ = _full_month(10, day_count=31)
        svc._client = AsyncMock()
        svc._client.get_schedule = AsyncMock(side_effect=[sep, oct_])

        days = await _fetch_upcoming_days(svc, "123", date(2026, 9, 28))

        assert svc._client.get_schedule.call_count == 2
        assert len(days) == 7  # 28,29,30 sep + 1,2,3,4 oct


class TestNotificationServiceDetectsChanges:
    @pytest.mark.asyncio
    async def test_detects_schedule_change(self):
        svc = ScheduleService("login", "pass")
        bot = AsyncMock()

        old_schedule = _full_month(9, lessons_on={14: [_lesson(classroom="301")]})
        new_schedule = _full_month(9, lessons_on={14: [_lesson(classroom="405")]})
        svc._client = AsyncMock()
        svc._client.get_schedule = AsyncMock(side_effect=[old_schedule, new_schedule])

        ns = NotificationService(bot, svc)

        with patch("services.notification_service.NotificationService._get_active_groups",
                   return_value={"123": "бв-601"}), \
                patch("services.notification_service.NotificationService._notify_group") as mock_notify, \
                patch("handlers.deps.today", return_value=date(2026, 9, 14)):
            await ns._take_snapshots()
            await ns._check_changes()

            mock_notify.assert_called_once()
            args = mock_notify.call_args
            assert args[0][0] == "123"
            assert len(args[0][2]) == 1  # one day with diff

    @pytest.mark.asyncio
    async def test_no_notification_on_same_schedule(self):
        svc = ScheduleService("login", "pass")
        bot = AsyncMock()

        schedule = _full_month(9, lessons_on={14: [_lesson()]})
        svc._client = AsyncMock()
        svc._client.get_schedule = AsyncMock(return_value=schedule)

        ns = NotificationService(bot, svc)

        with patch("services.notification_service.NotificationService._get_active_groups",
                   return_value={"123": "бв-601"}), \
                patch("services.notification_service.NotificationService._notify_group") as mock_notify, \
                patch("handlers.deps.today", return_value=date(2026, 9, 14)):
            await ns._take_snapshots()
            await ns._check_changes()

            mock_notify.assert_not_called()

    @pytest.mark.asyncio
    async def test_first_check_takes_snapshot_no_notify(self):
        svc = ScheduleService("login", "pass")
        bot = AsyncMock()

        schedule = _full_month(9, lessons_on={14: [_lesson()]})
        svc._client = AsyncMock()
        svc._client.get_schedule = AsyncMock(return_value=schedule)

        ns = NotificationService(bot, svc)

        with patch("services.notification_service.NotificationService._get_active_groups",
                   return_value={"123": "бв-601"}), \
                patch("services.notification_service.NotificationService._notify_group") as mock_notify, \
                patch("handlers.deps.today", return_value=date(2026, 9, 14)):
            await ns._take_snapshots()

            mock_notify.assert_not_called()
            assert "123" in ns._snapshots
