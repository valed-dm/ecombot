"""FSM states for profile handlers."""

from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup


class EditProfile(StatesGroup):
    getting_phone = State()
    getting_email = State()


class AddAddress(StatesGroup):
    getting_label = State()
    getting_address = State()
