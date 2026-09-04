from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from models import Event


def _extract_event(event: TelegramObject) -> tuple[int | None, str | None, str | None]:
    if isinstance(event, Message):
        user_id = event.from_user.id if event.from_user else None
        text = event.text or ""
        if text.startswith("/"):
            return user_id, text.split()[0].split("@")[0], None
        return user_id, "message", text[:128] or None

    if isinstance(event, CallbackQuery):
        user_id = event.from_user.id if event.from_user else None
        action = event.data or ""
        if len(action) > 64:
            return user_id, action[:64], action[64:]
        return user_id, action, None

    return None, None, None


class AnalyticsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_id, action, payload = _extract_event(event)

        if user_id and action and action != "noop":
            await Event.create(user_id=user_id, action=action, payload=payload)

        return await handler(event, data)
