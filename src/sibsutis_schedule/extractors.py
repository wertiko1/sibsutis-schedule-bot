import json
import logging
import re
from typing import Any

from .models import Lesson

logger: logging.Logger = logging.getLogger(__name__)

_PLAN_PATTERN: re.Pattern[str] = re.compile(r"(?<![_\w])days\[(\d+)\]\s*=\s*'(\{.*?\})'")
_FACT_PATTERN: re.Pattern[str] = re.compile(r"fact_schedule_days\[(\d+)\]\s*=\s*'(\{.*?\}|null)'")
_YEAR_PATTERN: re.Pattern[str] = re.compile(r"var currentYear\s*=\s*(\d+)")
_MONTH_PATTERN: re.Pattern[str] = re.compile(r"var currentMonth\s*=\s*(\d+)\s*-\s*1")


def extract_year_month(html: str) -> tuple[int, int]:
    """Extract the current year and month (1-indexed) from embedded JS variables"""
    year_match = _YEAR_PATTERN.search(html)
    month_match = _MONTH_PATTERN.search(html)

    if not year_match or not month_match:
        logger.error(
            "Could not extract year/month from page JS. "
            "year_match=%s, month_match=%s, html_snippet=%.500s",
            year_match, month_match, html,
        )
        raise RuntimeError("Could not extract year/month from the page JS.")

    year = int(year_match.group(1))
    month = int(month_match.group(1))

    logger.debug("Extracted year=%d, month=%d", year, month)
    return year, month


def extract_plan_days(html: str) -> dict[int, dict[str, Any]]:
    """Extract the planned schedule (days[1..14]) from embedded JS

    Keys 1-7 correspond to odd-week days (Mon-Sun),
    keys 8-14 correspond to even-week days
    """
    result: dict[int, dict[str, Any]] = {}
    for idx_str, json_str in _PLAN_PATTERN.findall(html):
        try:
            result[int(idx_str)] = json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning("Failed to decode plan JSON for days[%s]", idx_str)

    logger.debug("Extracted %d plan day entries", len(result))
    return result


def extract_fact_days(html: str) -> dict[int, dict[str, Any]]:
    """Extract the actual (fact) schedule overrides from embedded JS

    Returns a mapping of calendar day number to its parsed JSON data
    Entries with value 'null' are skipped
    """
    result: dict[int, dict[str, Any]] = {}
    for idx_str, json_str in _FACT_PATTERN.findall(html):
        if json_str == "null":
            continue
        try:
            result[int(idx_str)] = json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning("Failed to decode fact JSON for day %s", idx_str)

    logger.debug("Extracted %d fact day entries", len(result))
    return result


def parse_lessons(day_data: dict[str, Any]) -> list[Lesson]:
    """Parse a single day's JSON data into a list of Lesson models"""
    lessons: list[Lesson] = []

    for cell in day_data.get("ScheduleCell", []):
        if not isinstance(cell, dict):
            continue

        subgroups: list[dict[str, Any]] = cell.get("Subgroup", [])
        if not subgroups:
            continue

        time_begin: str = cell.get("DateBegin", "")[11:16]
        time_end: str = cell.get("DateEnd", "")[11:16]

        for sg in subgroups:
            lessons.append(Lesson(
                time_begin=time_begin,
                time_end=time_end,
                discipline=sg.get("DISCIPLINE", ""),
                lesson_type=sg.get("TYPE_LESSON", ""),
                teachers=sg.get("TEACHER", []),
                classroom=sg.get("CLASSROOM", ""),
                subgroup=sg.get("SUBGROUP"),
                weekday=sg.get("WEEK_DAY", ""),
            ))

    return lessons
