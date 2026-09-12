from aiogram import Router
from aiogram.types import ErrorEvent
from loguru import logger

from keyboards.schedule import back_to_main
from texts import messages

router = Router()


@router.errors()
async def on_error(event: ErrorEvent) -> None:
    logger.error("Handler error: {}", event.exception)

    text = messages.SCHEDULE_UNAVAILABLE
    kb = back_to_main()

    update = event.update
    if update.callback_query:
        await update.callback_query.message.answer(text, reply_markup=kb)
        await update.callback_query.answer()
    elif update.message:
        await update.message.answer(text, reply_markup=kb)
