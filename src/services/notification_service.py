import asyncio
from datetime import date, timedelta

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from loguru import logger

from keyboards.group import notification_keyboard
from models import User
from services.schedule_diff import DayDiff, diff_days
from services.schedule_service import ScheduleService
from sibsutis_schedule import DaySchedule
from texts import common, messages

CHECK_INTERVAL_SECONDS = 30 * 60  # 30 minutes
LOOKAHEAD_DAYS = 7


def _format_notification(group_name: str, diffs: list[DayDiff]) -> str:
    lines = [messages.NOTIFY_HEADER.format(group=group_name)]

    for diff in diffs:
        wd = common.WEEKDAYS_SHORT.get(diff.day.weekday, diff.day.weekday)
        lines.append(messages.NOTIFY_DAY.format(day=diff.day.day, month=diff.day.month, wd=wd))

        for lesson in diff.removed:
            lines.append(messages.NOTIFY_REMOVED.format(
                time=f"{lesson.time_begin}–{lesson.time_end}",
                name=lesson.discipline,
            ))
        for lesson in diff.added:
            lines.append(messages.NOTIFY_ADDED.format(
                time=f"{lesson.time_begin}–{lesson.time_end}",
                name=lesson.discipline,
            ))
        for old_l, new_l in diff.changed:
            parts = []
            if old_l.discipline != new_l.discipline:
                parts.append(f"{old_l.discipline} → {new_l.discipline}")
            else:
                parts.append(new_l.discipline)
            if old_l.classroom != new_l.classroom:
                parts.append(f"ауд. {old_l.classroom} → {new_l.classroom}")
            if old_l.teachers != new_l.teachers:
                parts.append("сменился преподаватель")
            lines.append(messages.NOTIFY_CHANGED.format(
                time=f"{new_l.time_begin}–{new_l.time_end}",
                name=" · ".join(parts),
            ))

    return "\n".join(lines)


async def _get_upcoming_days(
        schedule_service: ScheduleService, group: str, today_: date,
) -> list[DaySchedule]:
    days: list[DaySchedule] = []
    for offset in range(LOOKAHEAD_DAYS):
        d = today_ + timedelta(days=offset)
        schedule = await schedule_service.get_month(group, d.month)
        days.append(schedule.days[d.day - 1])
    return days


class NotificationService:
    def __init__(self, bot: Bot, schedule_service: ScheduleService) -> None:
        self._bot = bot
        self._schedule = schedule_service
        self._snapshots: dict[str, list[DaySchedule]] = {}  # group_id -> days
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._loop())
            logger.info("Notification service started (interval={}s)", CHECK_INTERVAL_SECONDS)

    async def _loop(self) -> None:
        # initial snapshot — no notifications on first run
        await self._take_snapshots()
        while True:
            await asyncio.sleep(CHECK_INTERVAL_SECONDS)
            await self._check_changes()

    async def _get_active_groups(self) -> dict[str, str]:
        users = (
            await User.filter(group_id__not_isnull=True, notify=True)
            .distinct()
            .values("group_id", "group_name")
        )
        return {u["group_id"]: u["group_name"] for u in users}

    async def _take_snapshots(self) -> None:
        from handlers.deps import today
        groups = await self._get_active_groups()
        today_ = today()
        for group_id in groups:
            try:
                days = await _get_upcoming_days(self._schedule, group_id, today_)
                self._snapshots[group_id] = days
            except Exception:
                logger.warning("Snapshot failed for group={}", group_id)

    async def _check_changes(self) -> None:
        from handlers.deps import today
        groups = await self._get_active_groups()
        today_ = today()

        for group_id, group_name in groups.items():
            try:
                new_days = await _get_upcoming_days(self._schedule, group_id, today_)
                old_days = self._snapshots.get(group_id)

                if old_days is None:
                    self._snapshots[group_id] = new_days
                    continue

                diffs = diff_days(old_days, new_days)
                self._snapshots[group_id] = new_days

                if diffs:
                    await self._notify_group(group_id, group_name, diffs)
            except Exception:
                logger.warning("Check failed for group={}", group_id)

    async def _notify_group(self, group_id: str, group_name: str, diffs: list[DayDiff]) -> None:
        text = _format_notification(group_name, diffs)
        kb = notification_keyboard()

        users = await User.filter(group_id=group_id, notify=True).values_list("user_id", flat=True)
        logger.info("Notifying {} users in group {} about schedule changes", len(users), group_name)

        for user_id in users:
            try:
                await self._bot.send_message(user_id, text, reply_markup=kb)
            except TelegramForbiddenError:
                logger.debug("User {} blocked the bot", user_id)
            except Exception:
                logger.warning("Failed to notify user {}", user_id)

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            self._task = None
