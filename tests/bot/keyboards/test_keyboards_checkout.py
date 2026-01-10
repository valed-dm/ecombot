"""
Unit tests for checkout keyboards.

This module verifies:
- Generation of the request contact keyboard (ReplyKeyboardMarkup).
- Generation of the checkout confirmation keyboard (slow path).
- Generation of the fast checkout confirmation keyboard (fast path).
"""

from aiogram.types import InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup
import pytest
from pytest_mock import MockerFixture

from ecombot.bot.callback_data import CheckoutCallbackFactory
from ecombot.bot.keyboards import checkout


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager to return predictable strings."""
    manager = mocker.patch("ecombot.bot.keyboards.checkout.manager")
    manager.get_message.side_effect = lambda section, key, **kwargs: f"[{key}]"
    return manager


def test_get_request_contact_keyboard(mock_manager):
    """Test the request contact keyboard."""
    keyboard = checkout.get_request_contact_keyboard()
    assert isinstance(keyboard, ReplyKeyboardMarkup)
    assert keyboard.resize_keyboard is True
    assert keyboard.one_time_keyboard is True

    button = keyboard.keyboard[0][0]
    assert button.request_contact is True
    assert button.text == "[share_phone]"


def test_get_checkout_confirmation_keyboard(mock_manager):
    """Test the slow path confirmation keyboard."""
    keyboard = checkout.get_checkout_confirmation_keyboard()
    assert isinstance(keyboard, InlineKeyboardMarkup)

    buttons = [btn for row in keyboard.inline_keyboard for btn in row]
    callbacks = [btn.callback_data for btn in buttons]

    assert CheckoutCallbackFactory(action="confirm").pack() in callbacks
    assert CheckoutCallbackFactory(action="cancel").pack() in callbacks


def test_get_fast_checkout_confirmation_keyboard(mock_manager):
    """Test the fast path confirmation keyboard."""
    keyboard = checkout.get_fast_checkout_confirmation_keyboard()
    assert isinstance(keyboard, InlineKeyboardMarkup)

    buttons = [btn for row in keyboard.inline_keyboard for btn in row]
    callbacks = [btn.callback_data for btn in buttons]

    assert CheckoutCallbackFactory(action="confirm").pack() in callbacks
    assert CheckoutCallbackFactory(action="edit_details").pack() in callbacks
    assert CheckoutCallbackFactory(action="cancel").pack() in callbacks
