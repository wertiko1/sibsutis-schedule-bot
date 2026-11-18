from datetime import date
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sibsutis_schedule.week_parity import academic_week_number, academic_week_parity


def test_academic_week_starts_with_week_containing_september_first():
    assert academic_week_number(date(2026, 9, 1)) == 1
    assert academic_week_number(date(2026, 9, 6)) == 1
    assert academic_week_number(date(2026, 9, 7)) == 2


def test_academic_week_continues_across_calendar_year():
    assert academic_week_number(date(2027, 1, 1)) == 18
    assert academic_week_parity(date(2027, 1, 1)) == "чётная"


def test_academic_week_parity():
    assert academic_week_parity(date(2026, 9, 1)) == "нечётная"
    assert academic_week_parity(date(2026, 9, 7)) == "чётная"
