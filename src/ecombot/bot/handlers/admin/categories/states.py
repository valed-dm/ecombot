"""FSM states for category management."""

from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup


class AddCategory(StatesGroup):
    """States for adding a new category."""

    name = State()
    description = State()


class DeleteCategory(StatesGroup):
    """States for deleting a category."""

    choose_category = State()
    confirm_deletion = State()
