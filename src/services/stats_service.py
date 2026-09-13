from datetime import datetime, timedelta

from tortoise.functions import Count

from config.stats import ACTION_LABELS, IGNORED_ACTIONS, PREFIX_LABELS
from models import Event, User
from schemas.stats import (
    ActionsStats, ActivityStats, AudienceStats, HubStats, PeriodDetail,
)

WEEKDAY_NAMES = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


def _day_start(dt: datetime) -> datetime:
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def _monday_of(dt: datetime) -> datetime:
    return _day_start(dt) - timedelta(days=dt.weekday())


# query helpers

async def _active_count(since: datetime, until: datetime | None = None) -> int:
    qs = Event.filter(created_at__gte=since)
    if until:
        qs = qs.filter(created_at__lt=until)
    rows = await qs.distinct().values_list("user_id", flat=True)
    return len(rows)


async def _event_count(since: datetime, until: datetime | None = None) -> int:
    qs = Event.filter(created_at__gte=since)
    if until:
        qs = qs.filter(created_at__lt=until)
    return await qs.count()


async def _new_users_count(since: datetime) -> int:
    from tortoise import Tortoise
    conn = Tortoise.get_connection("default")
    _, rows = await conn.execute_query(
        "SELECT COUNT(*) AS cnt FROM ("
        "  SELECT user_id FROM events GROUP BY user_id HAVING MIN(created_at) >= $1"
        ") sub",
        [since],
    )
    return rows[0]["cnt"] if rows else 0


async def _active_user_ids(since: datetime, until: datetime | None = None) -> set[int]:
    qs = Event.filter(created_at__gte=since)
    if until:
        qs = qs.filter(created_at__lt=until)
    rows = await qs.distinct().values_list("user_id", flat=True)
    return set(rows)


# queries

async def get_hub_stats(now: datetime) -> HubStats:
    today_start = _day_start(now)
    week_start = _monday_of(now)

    today_active = await _active_count(today_start)
    today_events = await _event_count(today_start)
    today_new = await _new_users_count(today_start)

    week_active = await _active_count(week_start)
    week_events = await _event_count(week_start)
    week_new = await _new_users_count(week_start)

    total_users = await User.all().count()
    users_with_group = await User.filter(group_id__not_isnull=True).count()

    return HubStats(
        today_active=today_active, today_events=today_events, today_new=today_new,
        week_active=week_active, week_events=week_events, week_new=week_new,
        total_users=total_users, users_with_group=users_with_group,
    )


async def get_activity_stats(now: datetime) -> ActivityStats:
    today_start = _day_start(now)
    yesterday_start = today_start - timedelta(days=1)
    week_start = _monday_of(now)
    prev_week_start = week_start - timedelta(weeks=1)

    today_events = await _event_count(today_start)
    today_active = await _active_count(today_start)
    yesterday_events = await _event_count(yesterday_start, today_start)

    week_events = await _event_count(week_start)
    week_active = await _active_count(week_start)
    prev_week_events = await _event_count(prev_week_start, week_start)

    today_trend = ((today_events - yesterday_events) / yesterday_events * 100) if yesterday_events else None
    week_trend = ((week_events - prev_week_events) / prev_week_events * 100) if prev_week_events else None

    # top weekday
    from tortoise import Tortoise
    conn = Tortoise.get_connection("default")
    _, rows = await conn.execute_query(
        "SELECT EXTRACT(isodow FROM created_at AT TIME ZONE 'UTC+7') AS dow, COUNT(*) AS cnt "
        "FROM events GROUP BY dow ORDER BY cnt DESC",
    )

    top_wd = None
    top_wd_pct = 0.0
    if rows:
        total = sum(r["cnt"] for r in rows)
        top = rows[0]
        dow_idx = int(top["dow"]) - 1  # isodow: 1=Mon, 7=Sun
        top_wd = WEEKDAY_NAMES[dow_idx] if 0 <= dow_idx < 7 else None
        top_wd_pct = round(top["cnt"] / total * 100, 1) if total else 0

    total_events = await Event.all().count()

    return ActivityStats(
        today=PeriodDetail(active=today_active, events=today_events, trend_pct=today_trend),
        week=PeriodDetail(active=week_active, events=week_events, trend_pct=week_trend),
        total_events=total_events,
        top_weekday=top_wd, top_weekday_pct=top_wd_pct,
    )


def _action_label(action: str) -> str | None:
    if action in IGNORED_ACTIONS:
        return None
    if action in ACTION_LABELS:
        return ACTION_LABELS[action]
    for prefix, label in PREFIX_LABELS:
        if action.startswith(prefix):
            return label
    return action


async def get_actions_stats() -> ActionsStats:
    top_actions_raw = (
        await Event.all()
        .exclude(action__in=IGNORED_ACTIONS)
        .annotate(cnt=Count("id"))
        .group_by("action")
        .order_by("-cnt")
        .values("action", "cnt")
    )

    merged: dict[str, int] = {}
    for row in top_actions_raw:
        label = _action_label(row["action"])
        if label:
            merged[label] = merged.get(label, 0) + row["cnt"]
    top_actions = sorted(merged.items(), key=lambda x: x[1], reverse=True)[:10]

    return ActionsStats(top_actions=top_actions)


async def get_audience_stats(now: datetime) -> AudienceStats:
    today_start = _day_start(now)
    week_start = _monday_of(now)
    month_start = _day_start(now.replace(day=1))
    prev_week_start = week_start - timedelta(weeks=1)

    total_users = await User.all().count()
    users_with_group = await User.filter(group_id__not_isnull=True).count()

    new_today = await _new_users_count(today_start)
    new_week = await _new_users_count(week_start)
    new_month = await _new_users_count(month_start)

    prev_users = await _active_user_ids(prev_week_start, week_start)
    curr_users = await _active_user_ids(week_start)
    retained = prev_users & curr_users

    prev_count = len(prev_users)
    retained_count = len(retained)
    pct = round(retained_count / prev_count * 100, 1) if prev_count else 0

    top_groups = (
        await User.filter(group_id__not_isnull=True)
        .annotate(cnt=Count("user_id"))
        .group_by("group_name")
        .order_by("-cnt")
        .limit(10)
        .values("group_name", "cnt")
    )

    return AudienceStats(
        total_users=total_users, users_with_group=users_with_group,
        new_today=new_today, new_week=new_week, new_month=new_month,
        retention_prev=prev_count, retention_retained=retained_count, retention_pct=pct,
        top_groups=list(top_groups),
    )
