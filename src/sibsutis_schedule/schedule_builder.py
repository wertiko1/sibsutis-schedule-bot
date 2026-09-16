import calendar
import logging
from datetime import date, datetime, timedelta, timezone
from typing import Any

from .constants import WEEKDAYS_RU
from .extractors import extract_fact_days, extract_plan_days, extract_year_month, parse_lessons
from .models import DaySchedule, Lesson, MonthSchedule
from .week_parity import compute_start_odd

logger: logging.Logger = logging.getLogger(__name__)


def _resolve_plan_key(day_date: date, is_odd_week: bool) -> int:
    """Map a calendar date to its plan-array index (1-7 odd, 8-14 even)"""
    dow: int = day_date.weekday() + 1
    if not is_odd_week:
        dow += 7
    return dow


def _is_in_project_period(lesson: Lesson, day_date: date) -> bool:
    """Check if a plan lesson should be skipped due to PROJECT_DATES"""
    for period in lesson.project_dates:
        try:
            parts_s = period.start_date.split("-")
            parts_e = period.end_date.split("-")
            if len(parts_s) == 3 and len(parts_e) == 3:
                start = date(int(parts_s[2]), int(parts_s[1]), int(parts_s[0]))
                end = date(int(parts_e[2]), int(parts_e[1]), int(parts_e[0]))
                if start <= day_date <= end:
                    return True
        except (ValueError, IndexError):
            continue
    return False


def _build_day(
        day_num: int,
        year: int,
        month: int,
        plan_days: dict[int, dict[str, Any]],
        fact_days: dict[int, dict[str, Any]],
        is_odd_week: bool,
) -> DaySchedule:
    """Build a DaySchedule by merging plan and fact data (matching website logic).

    1. Start with plan lessons, filtering out PROJECT_DATES entries
    2. For time slots present in fact: replace plan lessons with fact
    3. For time slots only in fact: add them
    """
    day_date: date = date(year, month, day_num)
    weekday_name: str = WEEKDAYS_RU[day_date.weekday()]

    # Collect plan lessons keyed by time_begin
    by_time: dict[str, list[Lesson]] = {}
    plan_key: int = _resolve_plan_key(day_date, is_odd_week)
    if plan_key in plan_days:
        for lesson in parse_lessons(plan_days[plan_key]):
            if _is_in_project_period(lesson, day_date):
                continue
            by_time.setdefault(lesson.time_begin, []).append(lesson)

    # Merge fact: replace or add by time slot
    fact_data: dict[str, Any] | None = fact_days.get(day_num)
    if fact_data and fact_data.get("ScheduleCell"):
        fact_lessons = parse_lessons(fact_data)
        fact_by_time: dict[str, list[Lesson]] = {}
        for lesson in fact_lessons:
            fact_by_time.setdefault(lesson.time_begin, []).append(lesson)

        for time_key, lessons in fact_by_time.items():
            by_time[time_key] = lessons

    # Flatten and sort by time
    lessons: list[Lesson] = []
    for time_key in sorted(by_time.keys()):
        lessons.extend(by_time[time_key])

    logger.debug("Day %d: %d lessons (plan_key=%d, has_fact=%s)", day_num, len(lessons), plan_key,
                 day_num in fact_days)

    for lesson in lessons:
        lesson.weekday = weekday_name

    return DaySchedule(
        day=day_num,
        month=month,
        year=year,
        weekday=weekday_name,
        lessons=lessons,
    )


def _resolve_year(month: int) -> int:
    """Determine the calendar year for a given academic month.

    Academic year: Sep-Dec belong to the current year,
    Jan-Aug belong to the next year.
    """
    _novo_tz = timezone(timedelta(hours=7))
    now = datetime.now(_novo_tz).date()
    academic_start = now.year if now.month >= 9 else now.year - 1
    if month >= 9:
        return academic_start
    return academic_start + 1


def build_schedule(html: str, group: str) -> MonthSchedule:
    """Parse the full schedule page HTML and build a MonthSchedule covering every day"""
    _, month = extract_year_month(html)
    year = _resolve_year(month)
    plan_days: dict[int, dict[str, Any]] = extract_plan_days(html)
    fact_days: dict[int, dict[str, Any]] = extract_fact_days(html)

    if not plan_days:
        raise RuntimeError("No plan schedule data found on the page.")

    num_days: int = calendar.monthrange(year, month)[1]
    is_odd_week: bool = compute_start_odd(year, month)

    logger.info("Building schedule for %s, %04d-%02d (%d days, start_odd=%s)", group, year, month, num_days,
                is_odd_week)

    days: list[DaySchedule] = []
    for day_num in range(1, num_days + 1):
        days.append(_build_day(day_num, year, month, plan_days, fact_days, is_odd_week))

        if date(year, month, day_num).weekday() == 6:
            is_odd_week = not is_odd_week

    return MonthSchedule(year=year, month=month, group=group, days=days)
