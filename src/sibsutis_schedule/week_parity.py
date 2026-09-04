from datetime import date


def _python_to_js_dow(d: date) -> int:
    """Convert Python weekday (0=Mon..6=Sun) to JS getDay() style (0=Sun, 1=Mon..6=Sat)"""
    return (d.weekday() + 1) % 7


def compute_start_odd(year: int, month: int) -> bool:
    """Determine whether the first day of the given month falls on an odd academic week

    Mirrors the JS parity logic used on sibsutis.ru, which counts weeks
    from October 2nd of the current academic year
    """
    m_js: int = month - 1

    if m_js >= 9:
        anchor = date(year, 10, 2)
    else:
        anchor = date(year - 1, 10, 2)

    anchor_dow: int = _python_to_js_dow(anchor)
    if anchor_dow == 0:
        add = 6
    elif anchor_dow == 1:
        add = 0
    else:
        add = anchor_dow

    first_day: date = date(year, month, 1)
    last_day_prev: date = date.fromordinal(first_day.toordinal() - 1)

    ldb_dow: int = _python_to_js_dow(last_day_prev)
    if ldb_dow == 0:
        sub = 1
    elif ldb_dow == 1:
        sub = 2
    else:
        sub = ldb_dow + 1

    diff_days: int = (first_day - anchor).days + add - sub
    return (diff_days / 7) % 2 != 1
