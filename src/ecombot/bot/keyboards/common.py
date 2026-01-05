"""Common keyboards used across multiple modules."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ecombot.core.manager import central_manager as manager

from ..callback_data import ConfirmationCallbackFactory


def get_delete_confirmation_keyboard(
    action: str,
    item_id: int,
) -> InlineKeyboardMarkup:
    """Builds a generic Yes/No confirmation keyboard for deletion."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text=manager.get_message("keyboards", "yes_delete"),
        callback_data=ConfirmationCallbackFactory(
            action=action,
            item_id=item_id,
            confirm=True,
        ),
    )
    builder.button(
        text=manager.get_message("keyboards", "no_go_back"),
        callback_data=ConfirmationCallbackFactory(
            action=action,
            item_id=item_id,
            confirm=False,
        ),
    )
    return builder.as_markup()


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """A simple keyboard with a single 'Cancel' button."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text=manager.get_message("keyboards", "cancel"), callback_data="cancel_fsm"
    )
    return builder.as_markup()
