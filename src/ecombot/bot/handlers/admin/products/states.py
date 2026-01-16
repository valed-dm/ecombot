"""FSM State definitions for admin handlers."""

from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup


class AddProduct(StatesGroup):
    choose_category = State()
    name = State()
    description = State()
    price = State()
    stock = State()
    get_image = State()


class EditProduct(StatesGroup):
    choose_category = State()
    choose_product = State()
    choose_field = State()
    get_new_value = State()
    get_new_image = State()


class DeleteProduct(StatesGroup):
    choose_category = State()
    choose_product = State()
    confirm_deletion = State()
