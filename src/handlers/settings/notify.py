from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards.group import settings_keyboard
from models import User
from texts import common, messages

router = Router()


@router.callback_query(F.data == "toggle_notify")
async def cb_toggle_notify(call: CallbackQuery, user: User) -> None:
    user.notify = not user.notify
    await user.save()
    text = messages.GROUP_CURRENT.format(
        group=user.group_name or "—",
        notify_status=common.NOTIFY_STATUS[user.notify],
    )
    await call.message.edit_text(text, reply_markup=settings_keyboard(user.notify))
    await call.answer()
