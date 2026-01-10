"""
Unit tests for admin navigation handlers.

This module verifies:
- FSM cancellation logic (via command and callback).
- Handling of 'no active state' scenarios.
- The /admin command handler and its error handling.
"""

from unittest.mock import AsyncMock

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery
from aiogram.types import Message
import pytest
from pytest_mock import MockerFixture

from ecombot.bot.handlers.admin import navigation


@pytest.fixture
def mock_send_panel(mocker: MockerFixture):
    return mocker.patch("ecombot.bot.handlers.admin.navigation.send_main_admin_panel")


async def test_cancel_fsm_no_state_message():
    """Test /cancel command when no state is active."""
    message = AsyncMock(spec=Message)
    message.answer = AsyncMock()
    state = AsyncMock()
    state.get_state.return_value = None

    await navigation.cancel_fsm_handler(message, state)

    state.clear.assert_not_awaited()
    message.answer.assert_awaited_once_with("You are not in an active process.")


async def test_cancel_fsm_no_state_callback():
    """Test cancel callback when no state is active."""
    query = AsyncMock(spec=CallbackQuery)
    query.answer = AsyncMock()
    state = AsyncMock()
    state.get_state.return_value = None

    await navigation.cancel_fsm_handler(query, state)

    state.clear.assert_not_awaited()
    query.answer.assert_awaited_once_with(
        "You are not in an active process.", show_alert=True
    )


async def test_cancel_fsm_active_message():
    """Test /cancel command with active state."""
    message = AsyncMock(spec=Message)
    message.answer = AsyncMock()
    state = AsyncMock()
    state.get_state.return_value = "SomeState"

    await navigation.cancel_fsm_handler(message, state)

    state.clear.assert_awaited_once()
    message.answer.assert_awaited_once_with(
        "Action cancelled. You have exited the current process."
    )


async def test_cancel_fsm_active_callback_success():
    """Test cancel callback with active state (successful edit)."""
    query = AsyncMock(spec=CallbackQuery)
    query.answer = AsyncMock()
    # Mock the message attribute of the callback query
    query.message = AsyncMock(spec=Message)
    query.message.edit_text = AsyncMock()

    state = AsyncMock()
    state.get_state.return_value = "SomeState"

    await navigation.cancel_fsm_handler(query, state)

    state.clear.assert_awaited_once()
    query.message.edit_text.assert_awaited_once_with("Action cancelled.")
    query.answer.assert_awaited_once()


async def test_cancel_fsm_active_callback_edit_fail():
    """Test cancel callback with active state (edit fails)."""
    query = AsyncMock(spec=CallbackQuery)
    query.answer = AsyncMock()
    query.message = AsyncMock(spec=Message)
    query.message.edit_text = AsyncMock()
    query.message.answer = AsyncMock()

    state = AsyncMock()
    state.get_state.return_value = "SomeState"

    # Simulate TelegramBadRequest when trying to edit
    query.message.edit_text.side_effect = TelegramBadRequest(
        method="edit", message="Error"
    )

    await navigation.cancel_fsm_handler(query, state)

    state.clear.assert_awaited_once()
    query.message.edit_text.assert_awaited_once()
    # Should fallback to answer()
    query.message.answer.assert_awaited_once_with("Action cancelled.")
    query.answer.assert_awaited_once()


async def test_command_admin_panel_success(mock_send_panel):
    """Test /admin command success."""
    message = AsyncMock()

    await navigation.command_admin_panel(message)

    mock_send_panel.assert_awaited_once_with(message)
    message.answer.assert_not_awaited()


async def test_command_admin_panel_failure(mock_send_panel):
    """Test /admin command failure."""
    message = AsyncMock()
    mock_send_panel.side_effect = Exception("Panel Error")

    await navigation.command_admin_panel(message)

    mock_send_panel.assert_awaited_once_with(message)
    message.answer.assert_awaited_once()
    assert "Failed to load admin panel" in message.answer.call_args[0][0]
