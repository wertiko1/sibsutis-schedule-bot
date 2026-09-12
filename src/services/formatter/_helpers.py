from datetime import time

from sibsutis_schedule import Lesson
from texts import common

_RU_VOWELS = frozenset("аеёиоуыэюяАЕЁИОУЫЭЮЯ")
_STOP_WORDS = {"и", "в", "на", "по", "для", "из", "к", "о", "от", "за", "при", "об"}


def _abbrev_word(word: str) -> str:
    if len(word) <= 4:
        return word
    if "-" in word:
        return "-".join(_abbrev_word(p) for p in word.split("-"))
    for end in range(4, 2, -1):
        if word[end - 1] not in _RU_VOWELS:
            return word[:end] + "."
    return word[:3] + "."


def shorten(name: str, max_len: int) -> str:
    if len(name) <= max_len:
        return name

    words = name.split()

    if len(words) > 2:
        filtered = [w for w in words if w.lower() not in _STOP_WORDS]
        if len(filtered) >= 2:
            words = filtered
        if len(" ".join(words)) <= max_len:
            return " ".join(words)

    while len(" ".join(words)) > max_len:
        longest_idx = -1
        longest_len = 4
        for i, w in enumerate(words):
            if not w.endswith(".") and len(w) > longest_len:
                longest_len = len(w)
                longest_idx = i
        if longest_idx == -1:
            break
        words[longest_idx] = _abbrev_word(words[longest_idx])

    result = " ".join(words)
    if len(result) > max_len:
        return result[:max_len - 1] + "…"
    return result


def parse_time(s: str) -> time:
    h, m = s.split(":")
    return time(int(h), int(m))


def minutes_between(a: time, b: time) -> int:
    return (b.hour * 60 + b.minute) - (a.hour * 60 + a.minute)


def format_minutes(m: int) -> str:
    if m < 60:
        return common.TIME_MINUTES.format(m=m)
    h, mins = divmod(m, 60)
    if mins == 0:
        return common.TIME_HOURS.format(h=h)
    return common.TIME_HOURS_MINUTES.format(h=h, m=mins)


def lesson_word(n: int) -> str:
    if 11 <= n % 100 <= 14:
        return "пар"
    last = n % 10
    if last == 1:
        return "пара"
    if 2 <= last <= 4:
        return "пары"
    return "пар"


def group_lessons(lessons: list[Lesson]) -> list[list[Lesson]]:
    groups: list[list[Lesson]] = []
    for lesson in lessons:
        if (
                groups
                and groups[-1][0].time_begin == lesson.time_begin
                and groups[-1][0].time_end == lesson.time_end
        ):
            groups[-1].append(lesson)
        else:
            groups.append([lesson])
    return groups
