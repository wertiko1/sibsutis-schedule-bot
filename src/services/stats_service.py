from datetime import datetime, timedelta

from tortoise.functions import Count

from config.stats import ACTION_LABELS, IGNORED_ACTIONS, PREFIX_LABELS
from models import Event, User
from texts import messages


def _action_label(action: str) -> str | None:
    if action in IGNORED_ACTIONS:
        return None
    if action in ACTION_LABELS:
        return ACTION_LABELS[action]
    for prefix, label in PREFIX_LABELS:
        if action.startswith(prefix):
            return label
    return action


async def get_stats(now: datetime) -> str:
    day_ago = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)

    total_users = await User.all().count()
    users_with_group = await User.filter(group_id__not_isnull=True).count()

    events_today = await Event.filter(created_at__gte=day_ago).count()
    events_week = await Event.filter(created_at__gte=week_ago).count()
    events_total = await Event.all().count()

    active_today = (
        await Event.filter(created_at__gte=day_ago)
        .distinct()
        .values_list("user_id", flat=True)
    )
    active_week = (
        await Event.filter(created_at__gte=week_ago)
        .distinct()
        .values_list("user_id", flat=True)
    )
    active_total = (
        await Event.all()
        .distinct()
        .values_list("user_id", flat=True)
    )

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

    top_groups = (
        await User.filter(group_id__not_isnull=True)
        .annotate(cnt=Count("user_id"))
        .group_by("group_name")
        .order_by("-cnt")
        .limit(10)
        .values("group_name", "cnt")
    )

    periods = [
        ("День", len(active_today), events_today),
        ("Неделя", len(active_week), events_week),
        ("Всего", len(active_total), events_total),
    ]

    lines = [
        messages.STATS_HEADER,
        "",
        messages.STATS_USERS.format(total=total_users, with_group=users_with_group),
        "",
    ]
    for period, active, events in periods:
        lines.append(messages.STATS_PERIOD.format(period=period, active=active, events=events))

    lines.append("")
    lines.append(messages.STATS_TOP_ACTIONS)
    for label, cnt in top_actions:
        lines.append(f"{label} — <code>{cnt}</code>")

    if top_groups:
        lines.append("")
        lines.append(messages.STATS_TOP_GROUPS)
        for row in top_groups:
            lines.append(f"{row['group_name']} — {row['cnt']} чел.")

    return "\n".join(lines)
