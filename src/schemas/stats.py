from dataclasses import dataclass


@dataclass
class HubStats:
    today_active: int
    today_events: int
    today_new: int
    week_active: int
    week_events: int
    week_new: int
    total_users: int
    users_with_group: int


@dataclass
class PeriodDetail:
    active: int
    events: int
    trend_pct: float | None


@dataclass
class ActivityStats:
    today: PeriodDetail
    week: PeriodDetail
    top_weekday: str | None
    top_weekday_pct: float


@dataclass
class ActionsStats:
    top_actions: list[tuple[str, int]]


@dataclass
class AudienceStats:
    total_users: int
    users_with_group: int
    new_today: int
    new_week: int
    new_month: int
    retention_prev: int
    retention_retained: int
    retention_pct: float
    top_groups: list[dict]
