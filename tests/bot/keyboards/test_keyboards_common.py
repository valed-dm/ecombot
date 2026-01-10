"""
Unit tests for common keyboards.

This module verifies:
- Generation of the generic delete confirmation keyboard.
- Generation of the generic cancel keyboard.
"""

from aiogram.types import InlineKeyboardMarkup
import pytest
from pytest_mock import MockerFixture

from ecombot.bot.callback_data import ConfirmationCallbackFactory
from ecombot.bot.keyboards import common


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager to return predictable strings."""
    manager = mocker.patch("ecombot.bot.keyboards.common.manager")
    manager.get_message.side_effect = lambda section, key, **kwargs: f"[{key}]"
    return manager


def test_get_delete_confirmation_keyboard(mock_manager):
    """Test the delete confirmation keyboard."""
    action = "delete_item"
    item_id = 123

    keyboard = common.get_delete_confirmation_keyboard(action, item_id)
    assert isinstance(keyboard, InlineKeyboardMarkup)

    buttons = [btn for row in keyboard.inline_keyboard for btn in row]
    callbacks = [btn.callback_data for btn in buttons]
    texts = [btn.text for btn in buttons]

    assert "[yes_delete]" in texts
    assert "[no_go_back]" in texts

    expected_yes = ConfirmationCallbackFactory(
        action=action, item_id=item_id, confirm=True
    ).pack()
    expected_no = ConfirmationCallbackFactory(
        action=action, item_id=item_id, confirm=False
    ).pack()

    assert expected_yes in callbacks
    assert expected_no in callbacks


def test_get_cancel_keyboard(mock_manager):
    """Test the cancel keyboard."""
    keyboard = common.get_cancel_keyboard()
    assert isinstance(keyboard, InlineKeyboardMarkup)

    buttons = [btn for row in keyboard.inline_keyboard for btn in row]
    callbacks = [btn.callback_data for btn in buttons]
    texts = [btn.text for btn in buttons]

    assert "[cancel]" in texts
    assert "cancel_fsm" in callbacks
