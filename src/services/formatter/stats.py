from datetime import datetime, timedelta

from services.stats_service import (
    ActionsStats, ActivityStats, AudienceStats, HubStats,
    _day_start, _monday_of,
)
from texts import common, messages


def format_hub(data: HubStats, now: datetime) -> str:
    today_date = f"{now.day:02d}.{now.month:02d}"
    week_start = _monday_of(now)
    week_end = week_start + timedelta(days=6)

    lines = [
        messages.STATS_HUB_HEADER,
        "",
        messages.STATS_HUB_TODAY.format(date=today_date, active=data.today_active, events=data.today_events,
                                        new=data.today_new),
        "",
        messages.STATS_HUB_WEEK.format(
            start=f"{week_start.day:02d}.{week_start.month:02d}",
            end=f"{week_end.day:02d}.{week_end.month:02d}",
            active=data.week_active, events=data.week_events, new=data.week_new,
        ),
        "",
        messages.STATS_HUB_TOTAL.format(total=data.total_users, with_group=data.users_with_group),
    ]
    return "\n".join(lines)


def _format_trend(pct: float | None, vs: str) -> str:
    if pct is None:
        return messages.STATS_ACT_TREND_NA
    arrow = "↑" if pct >= 0 else "↓"
    return messages.STATS_ACT_TREND.format(arrow=arrow, pct=f"{abs(pct):.0f}", vs=vs)


def format_activity(data: ActivityStats, now: datetime) -> str:
    today_date = f"{now.day:02d}.{now.month:02d}"
    wd = common.WEEKDAY_HEADERS[now.weekday()]
    week_start = _monday_of(now)
    week_end = week_start + timedelta(days=6)

    lines = [
        messages.STATS_ACT_HEADER,
        "",
        messages.STATS_ACT_TODAY.format(wd=wd, date=today_date, active=data.today.active, events=data.today.events),
        _format_trend(data.today.trend_pct, "вчера"),
        "",
        messages.STATS_ACT_WEEK.format(
            start=f"{week_start.day:02d}.{week_start.month:02d}",
            end=f"{week_end.day:02d}.{week_end.month:02d}",
            active=data.week.active, events=data.week.events,
        ),
        _format_trend(data.week.trend_pct, "прошлая неделя"),
    ]

    if data.top_weekday:
        lines.append("")
        lines.append(messages.STATS_ACT_TOP_DAY.format(wd=data.top_weekday, pct=data.top_weekday_pct))

    return "\n".join(lines)


def format_actions(data: ActionsStats) -> str:
    lines = [messages.STATS_ACTIONS_HEADER]
    for label, cnt in data.top_actions:
        lines.append(f"{label} — <code>{cnt}</code>")
    return "\n".join(lines)


def format_audience(data: AudienceStats) -> str:
    lines = [
        messages.STATS_AUD_HEADER,
        "",
        messages.STATS_AUD_TOTAL.format(total=data.total_users, with_group=data.users_with_group),
        "",
        messages.STATS_AUD_NEW_HEADER,
        messages.STATS_AUD_NEW_LINE.format(period="Сегодня", count=data.new_today),
        messages.STATS_AUD_NEW_LINE.format(period="За неделю", count=data.new_week),
        messages.STATS_AUD_NEW_LINE.format(period="За месяц", count=data.new_month),
        "",
        messages.STATS_AUD_RET_HEADER,
        messages.STATS_AUD_RET.format(
            prev=data.retention_prev,
            retained=data.retention_retained,
            pct=data.retention_pct,
        ),
    ]

    if data.top_groups:
        lines.append("")
        lines.append(messages.STATS_GROUPS_HEADER)
        for row in data.top_groups:
            lines.append(f"{row['group_name']} — {row['cnt']} чел.")

    return "\n".join(lines)
