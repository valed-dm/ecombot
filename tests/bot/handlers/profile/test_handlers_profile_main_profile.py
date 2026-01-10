"""
Unit tests for main profile handlers.

This module verifies:
- Displaying the profile (command and callback).
- Editing phone number flow.
- Editing email flow.
"""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from aiogram.fsm.context import FSMContext
import pytest
from pytest_mock import MockerFixture

from ecombot.bot.handlers.profile import main_profile
from ecombot.bot.handlers.profile.states import EditProfile
from ecombot.db.models import User


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager."""
    manager = mocker.patch("ecombot.bot.handlers.profile.main_profile.manager")
    manager.get_message.return_value = "Message text"
    return manager


@pytest.fixture
def mock_user_service(mocker: MockerFixture):
    """Mocks the user service."""
    return mocker.patch("ecombot.bot.handlers.profile.main_profile.user_service")


@pytest.fixture
def mock_utils(mocker: MockerFixture):
    """Mocks profile utils."""
    return mocker.patch(
        "ecombot.bot.handlers.profile.main_profile.format_profile_text",
        return_value="Profile Text",
    )


@pytest.fixture
def mock_keyboards(mocker: MockerFixture):
    """Mocks keyboard generators."""
    mocker.patch("ecombot.bot.handlers.profile.main_profile.get_profile_keyboard")
    mocker.patch("ecombot.bot.handlers.profile.main_profile.get_cancel_keyboard")


async def test_profile_handler_success(
    mock_manager, mock_user_service, mock_utils, mock_keyboards, mock_session
):
    """Test displaying the profile via command."""
    message = AsyncMock()
    db_user = MagicMock(spec=User)

    mock_profile = MagicMock()
    mock_user_service.get_user_profile = AsyncMock(return_value=mock_profile)

    await main_profile.profile_handler(message, mock_session, db_user)

    mock_user_service.get_user_profile.assert_awaited_once_with(mock_session, db_user)
    mock_utils.assert_called_once_with(mock_profile)
    message.answer.assert_awaited_once()


async def test_back_to_profile_handler_success(
    mock_manager, mock_user_service, mock_utils, mock_keyboards, mock_session
):
    """Test returning to profile via callback."""
    query = AsyncMock()
    callback_message = AsyncMock()
    db_user = MagicMock(spec=User)

    mock_profile = MagicMock()
    mock_user_service.get_user_profile = AsyncMock(return_value=mock_profile)

    await main_profile.back_to_profile_handler(
        query, mock_session, db_user, callback_message
    )

    callback_message.edit_text.assert_awaited_once()
    query.answer.assert_awaited_once()


async def test_edit_phone_start(mock_manager, mock_keyboards):
    """Test starting phone edit flow."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock(spec=FSMContext)

    await main_profile.edit_phone_start(query, state, callback_message)

    callback_message.edit_text.assert_awaited_once()
    state.set_state.assert_awaited_once_with(EditProfile.getting_phone)
    query.answer.assert_awaited_once()


async def test_edit_phone_get_phone_success(
    mock_manager, mock_user_service, mock_utils, mock_keyboards, mock_session
):
    """Test receiving new phone number."""
    message = AsyncMock()
    message.text = "1234567890"
    state = AsyncMock(spec=FSMContext)
    db_user = MagicMock(spec=User)
    db_user.id = 123

    mock_user_service.update_profile_details = AsyncMock()
    mock_user_service.get_user_profile = AsyncMock(return_value=MagicMock())

    await main_profile.edit_phone_get_phone(message, state, mock_session, db_user)

    # Verify update call
    mock_user_service.update_profile_details.assert_awaited_once_with(
        session=mock_session, user_id=123, update_data={"phone": "1234567890"}
    )
    # Verify success message
    message.answer.assert_awaited()
    # Verify refresh
    mock_session.refresh.assert_awaited_once_with(db_user)
    # Verify cleanup
    message.delete.assert_awaited_once()
    state.clear.assert_awaited_once()

    # Verify profile re-display (profile_handler logic)
    # message.answer is called twice: once for success msg, once for profile view
    assert message.answer.await_count == 2


async def test_edit_email_start(mock_manager, mock_keyboards):
    """Test starting email edit flow."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock(spec=FSMContext)

    await main_profile.edit_email_start(query, state, callback_message)

    callback_message.edit_text.assert_awaited_once()
    state.set_state.assert_awaited_once_with(EditProfile.getting_email)
    query.answer.assert_awaited_once()


async def test_edit_email_get_email_success(
    mock_manager, mock_user_service, mock_utils, mock_keyboards, mock_session
):
    """Test receiving new email."""
    message = AsyncMock()
    message.text = "test@example.com"
    state = AsyncMock(spec=FSMContext)
    db_user = MagicMock(spec=User)
    db_user.id = 123

    mock_user_service.update_profile_details = AsyncMock()
    mock_user_service.get_user_profile = AsyncMock(return_value=MagicMock())

    await main_profile.edit_email_get_email(message, state, mock_session, db_user)

    mock_user_service.update_profile_details.assert_awaited_once_with(
        session=mock_session, user_id=123, update_data={"email": "test@example.com"}
    )
    message.answer.assert_awaited()
    mock_session.refresh.assert_awaited_once_with(db_user)
    message.delete.assert_awaited_once()
    state.clear.assert_awaited_once()
    assert message.answer.await_count == 2


async def test_edit_email_get_email_error(
    mock_manager, mock_user_service, mock_session
):
    """Test error handling during email update."""
    message = AsyncMock()
    message.text = "test@example.com"
    state = AsyncMock(spec=FSMContext)
    db_user = MagicMock(spec=User)
    db_user.id = 123

    mock_user_service.update_profile_details.side_effect = Exception("DB Error")

    await main_profile.edit_email_get_email(message, state, mock_session, db_user)

    message.answer.assert_awaited_once()  # Error message
    mock_session.refresh.assert_not_awaited()
    message.delete.assert_not_awaited()
    state.clear.assert_awaited_once()
