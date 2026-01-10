"""
Unit tests for profile navigation handlers.

This module verifies:
- The 'do nothing' handler.
- FSM cancellation logic (via command and callback) specific to the profile module.
"""

from unittest.mock import AsyncMock

from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message

from ecombot.bot.handlers.profile import navigation


async def test_do_nothing_handler():
    """Test the do_nothing handler."""
    query = AsyncMock(spec=CallbackQuery)
    query.answer = AsyncMock()
    await navigation.do_nothing_handler(query)
    query.answer.assert_awaited_once()


async def test_cancel_fsm_no_state_message():
    """Test /cancel command when no state is active."""
    message = AsyncMock(spec=Message)
    message.answer = AsyncMock()
    state = AsyncMock(spec=FSMContext)
    state.get_state = AsyncMock(return_value=None)

    await navigation.cancel_fsm_handler(message, state)

    state.clear.assert_not_awaited()
    message.answer.assert_awaited_once_with("You are not in an active process.")


async def test_cancel_fsm_no_state_callback():
    """Test cancel callback when no state is active."""
    query = AsyncMock(spec=CallbackQuery)
    query.answer = AsyncMock()
    state = AsyncMock(spec=FSMContext)
    state.get_state = AsyncMock(return_value=None)

    await navigation.cancel_fsm_handler(query, state)

    state.clear.assert_not_awaited()
    query.answer.assert_awaited_once_with(
        "You are not in an active process.", show_alert=True
    )


async def test_cancel_fsm_active_message():
    """Test /cancel command with active state."""
    message = AsyncMock(spec=Message)
    message.answer = AsyncMock()
    state = AsyncMock(spec=FSMContext)
    state.get_state = AsyncMock(return_value="SomeState")
    state.clear = AsyncMock()

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

    state = AsyncMock(spec=FSMContext)
    state.get_state = AsyncMock(return_value="SomeState")
    state.clear = AsyncMock()

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

    state = AsyncMock(spec=FSMContext)
    state.get_state = AsyncMock(return_value="SomeState")
    state.clear = AsyncMock()

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
