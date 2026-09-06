from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from keyboards.group import onboarding_keyboard
from models import User
from texts import messages

_GROUP_CALLBACKS = {"grp_", "change_group", "cancel_group"}


def _get_tg_user(event: TelegramObject):
    if isinstance(event, (Message, CallbackQuery)):
        return event.from_user
    return None


async def _is_allowed_without_group(event: TelegramObject, data: dict[str, Any]) -> bool:
    if isinstance(event, Message):
        state = data.get("state")
        if state and await state.get_state() is not None:
            return True
        return bool(event.text and (event.text.startswith("/start") or event.text.startswith("/help")))

    if isinstance(event, CallbackQuery):
        cb = event.data or ""
        return any(cb.startswith(p) for p in _GROUP_CALLBACKS)

    return False


class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user = _get_tg_user(event)
        if not tg_user:
            return await handler(event, data)

        user, _ = await User.get_or_create(user_id=tg_user.id)
        data["user"] = user

        if not user.group_id and not await _is_allowed_without_group(event, data):
            if isinstance(event, Message):
                await event.answer(messages.NO_GROUP, reply_markup=onboarding_keyboard())
            elif isinstance(event, CallbackQuery):
                await event.answer(messages.NO_GROUP, show_alert=True)
            return

        return await handler(event, data)
