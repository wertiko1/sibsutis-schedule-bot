from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.group import cancel_keyboard, group_results_keyboard, onboarding_keyboard, settings_keyboard
from keyboards.schedule import back_to_main
from models import User
from states import GroupStates
from texts import common, messages
from handlers.deps import service

router = Router()


@router.callback_query(F.data == "change_group")
async def cb_change_group(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(GroupStates.waiting_for_search)
    await call.message.edit_text(
        messages.GROUP_SELECT,
        reply_markup=cancel_keyboard(),
    )
    await call.answer()


@router.callback_query(F.data == "cancel_group")
async def cb_cancel_group(call: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.clear()
    if user.group_id:
        await call.message.edit_text(
            messages.GROUP_CURRENT.format(
                group=user.group_name,
                notify_status=common.NOTIFY_STATUS[user.notify],
            ),
            reply_markup=settings_keyboard(user.notify),
        )
    else:
        await call.message.edit_text(
            messages.ONBOARDING,
            reply_markup=onboarding_keyboard(),
        )
    await call.answer()


@router.message(GroupStates.waiting_for_search)
async def on_group_search(message: Message, state: FSMContext) -> None:
    query = message.text.strip()
    if not query:
        return

    groups = await service.search_groups(query)
    if not groups:
        await message.answer(messages.GROUP_NOT_FOUND.format(query=query))
        return

    await state.update_data(search_results=groups, search_query=query)
    await message.answer(
        messages.GROUP_SEARCH_RESULTS.format(query=query),
        reply_markup=group_results_keyboard(groups),
    )


@router.callback_query(F.data.regexp(r"^grp_page_\d+$"))
async def cb_group_page(call: CallbackQuery, state: FSMContext) -> None:
    page = int(call.data.split("_")[2])
    data = await state.get_data()
    groups = data.get("search_results", [])
    query = data.get("search_query", "")

    await call.message.edit_text(
        messages.GROUP_SEARCH_RESULTS.format(query=query),
        reply_markup=group_results_keyboard(groups, page=page),
    )
    await call.answer()


@router.callback_query(F.data.startswith("grp_"))
async def cb_select_group(call: CallbackQuery, state: FSMContext, user: User) -> None:
    group_id = call.data.split("_", 1)[1]

    data = await state.get_data()
    groups = data.get("search_results", [])
    group_name = group_id
    for g in groups:
        if g["id"] == group_id:
            group_name = g["text"]
            break

    is_new = not user.group_id
    user.group_id = group_id
    user.group_name = group_name
    await user.save(update_fields=["group_id", "group_name"])
    await state.clear()

    if is_new:
        text = messages.GROUP_SELECTED.format(group=group_name)
    else:
        text = messages.GROUP_CHANGED.format(group=group_name)

    await call.message.edit_text(text, reply_markup=back_to_main())
    await call.answer()
