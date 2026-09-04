from aiogram.fsm.state import State, StatesGroup


class GroupStates(StatesGroup):
    waiting_for_search = State()
