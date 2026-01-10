"""
Unit tests for profile keyboards.

This module verifies:
- Generation of the main profile keyboard.
- Generation of the address details keyboard.
- Generation of the address management keyboard (handling default vs non-default
  addresses).
"""

from unittest.mock import MagicMock

from aiogram.types import InlineKeyboardMarkup
import pytest
from pytest_mock import MockerFixture

from ecombot.bot.callback_data import ProfileCallbackFactory
from ecombot.bot.keyboards import profile
from ecombot.schemas.dto import DeliveryAddressDTO


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager to return predictable strings."""
    manager = mocker.patch("ecombot.bot.keyboards.profile.manager")
    manager.get_message.side_effect = lambda section, key, **kwargs: f"[{key}]"
    return manager


def test_get_profile_keyboard(mock_manager):
    """Test the main profile keyboard."""
    keyboard = profile.get_profile_keyboard()
    assert isinstance(keyboard, InlineKeyboardMarkup)

    buttons = [btn for row in keyboard.inline_keyboard for btn in row]
    callbacks = [btn.callback_data for btn in buttons]

    assert ProfileCallbackFactory(action="edit_phone").pack() in callbacks
    assert ProfileCallbackFactory(action="edit_email").pack() in callbacks
    assert ProfileCallbackFactory(action="manage_addr").pack() in callbacks


def test_get_address_details_keyboard(mock_manager):
    """Test the address details keyboard."""
    keyboard = profile.get_address_details_keyboard()
    assert isinstance(keyboard, InlineKeyboardMarkup)

    buttons = [btn for row in keyboard.inline_keyboard for btn in row]
    callbacks = [btn.callback_data for btn in buttons]

    assert ProfileCallbackFactory(action="manage_addr").pack() in callbacks


def test_get_address_management_keyboard_empty(mock_manager):
    """Test address management keyboard with no addresses."""
    keyboard = profile.get_address_management_keyboard([])
    assert isinstance(keyboard, InlineKeyboardMarkup)

    buttons = [btn for row in keyboard.inline_keyboard for btn in row]
    callbacks = [btn.callback_data for btn in buttons]

    assert ProfileCallbackFactory(action="add_addr").pack() in callbacks
    assert ProfileCallbackFactory(action="profile_back_main").pack() in callbacks


def test_get_address_management_keyboard_populated(mock_manager):
    """Test address management keyboard with addresses."""
    # Address 1: Default
    addr1 = MagicMock(spec=DeliveryAddressDTO)
    addr1.id = 10
    addr1.is_default = True
    addr1.address_label = "Home"

    # Address 2: Not Default
    addr2 = MagicMock(spec=DeliveryAddressDTO)
    addr2.id = 11
    addr2.is_default = False
    addr2.address_label = "Work"

    keyboard = profile.get_address_management_keyboard([addr1, addr2])

    buttons = [btn for row in keyboard.inline_keyboard for btn in row]
    callbacks = [btn.callback_data for btn in buttons]

    # Check Address 1 (Default)
    # Should have View and Delete, but NOT Set Default
    assert ProfileCallbackFactory(action="view_addr", address_id=10).pack() in callbacks
    assert (
        ProfileCallbackFactory(action="delete_addr", address_id=10).pack() in callbacks
    )
    assert (
        ProfileCallbackFactory(action="set_default_addr", address_id=10).pack()
        not in callbacks
    )

    # Check Address 2 (Not Default)
    # Should have View, Set Default, and Delete
    assert ProfileCallbackFactory(action="view_addr", address_id=11).pack() in callbacks
    assert (
        ProfileCallbackFactory(action="set_default_addr", address_id=11).pack()
        in callbacks
    )
    assert (
        ProfileCallbackFactory(action="delete_addr", address_id=11).pack() in callbacks
    )

    # Check static buttons
    assert ProfileCallbackFactory(action="add_addr").pack() in callbacks
    assert ProfileCallbackFactory(action="profile_back_main").pack() in callbacks
