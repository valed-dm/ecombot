from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup


class PickupPointStates(StatesGroup):
    """FSM for creating a new pickup point."""

    waiting_for_name = State()
    waiting_for_address = State()
    waiting_for_type = State()
    waiting_for_hours = State()
