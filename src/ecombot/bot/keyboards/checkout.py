"""Checkout-related keyboards."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.types import KeyboardButton
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ecombot.core.manager import central_manager as manager

from ..callback_data import CheckoutCallbackFactory


def get_request_contact_keyboard() -> ReplyKeyboardMarkup:
    """
    Builds a reply keyboard with a single button to request the user's contact.
    This is a special button type that prompts the user to share their phone number.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=manager.get_message("keyboards", "share_phone"),
                    request_contact=True,
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_checkout_confirmation_keyboard() -> InlineKeyboardMarkup:
    """
    Builds the final Yes/No keyboard for confirming the order,
    used in the "slow path" FSM.
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text=manager.get_message("keyboards", "confirm"),
        callback_data=CheckoutCallbackFactory(action="confirm"),
    )
    builder.button(
        text=manager.get_message("keyboards", "cancel_short"),
        callback_data=CheckoutCallbackFactory(action="cancel"),
    )
    builder.adjust(2)
    return builder.as_markup()


def get_fast_checkout_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Builds the keyboard for the 'fast path' checkout confirmation."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text=manager.get_message("keyboards", "confirm_order"),
        callback_data=CheckoutCallbackFactory(action="confirm"),
    )
    builder.button(
        text=manager.get_message("keyboards", "edit_details"),
        callback_data=CheckoutCallbackFactory(action="edit_details"),
    )
    builder.button(
        text=manager.get_message("keyboards", "cancel"),
        callback_data=CheckoutCallbackFactory(action="cancel"),
    )
    builder.adjust(1)
    return builder.as_markup()
