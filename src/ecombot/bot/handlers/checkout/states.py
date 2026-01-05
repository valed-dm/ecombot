"""Checkout FSM states."""

from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup


class CheckoutFSM(StatesGroup):
    # States for the "slow path" / first-time user
    getting_name = State()
    getting_phone = State()
    getting_address = State()
    confirm_slow_path = State()

    # State for the "fast path" / returning user
    confirm_fast_path = State()
