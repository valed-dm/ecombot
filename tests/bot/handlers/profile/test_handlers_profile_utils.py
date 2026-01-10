"""
Unit tests for profile utilities.

This module verifies:
- Text formatting for the main profile view.
- Text formatting for the address management view.
- Sending/editing the address management view with fallback logic.
"""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from aiogram.exceptions import TelegramBadRequest
import pytest
from pytest_mock import MockerFixture

from ecombot.bot.handlers.profile import utils
from ecombot.db.models import DeliveryAddress
from ecombot.db.models import User


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager."""
    manager = mocker.patch("ecombot.bot.handlers.profile.utils.manager")
    manager.get_message.side_effect = lambda section, key, **kwargs: f"[{key}]"
    return manager


@pytest.fixture
def mock_user_service(mocker: MockerFixture):
    """Mocks the user service."""
    return mocker.patch("ecombot.bot.handlers.profile.utils.user_service")


@pytest.fixture
def mock_keyboards(mocker: MockerFixture):
    """Mocks the keyboard generator."""
    return mocker.patch(
        "ecombot.bot.handlers.profile.utils.get_address_management_keyboard"
    )


def test_format_profile_text_full(mock_manager):
    """Test formatting profile with all details."""
    addr = MagicMock(spec=DeliveryAddress)
    addr.is_default = True
    addr.full_address = "123 Main St"

    user_profile = MagicMock(spec=User)
    user_profile.first_name = "John"
    user_profile.phone = "1234567890"
    user_profile.email = "john@example.com"
    user_profile.addresses = [addr]

    text = utils.format_profile_text(user_profile)

    assert "[profile_header]" in text
    assert "[profile_template]" in text
    # The address is appended directly
    assert "123 Main St" in text


def test_format_profile_text_missing_info(mock_manager):
    """Test formatting profile with missing phone, email, and default address."""
    user_profile = MagicMock(spec=User)
    user_profile.first_name = "John"
    user_profile.phone = None
    user_profile.email = None
    user_profile.addresses = []

    text = utils.format_profile_text(user_profile)

    # Should use fallback text for missing address
    assert "[default_address_not_set]" in text
    # Phone/Email fallbacks are passed to template, so we verify the manager call
    # implicitly by ensuring no crash, but we can check if [not_set_text] was retrieved
    mock_manager.get_message.assert_any_call("profile", "not_set_text")


def test_format_address_management_text_empty(mock_manager):
    """Test formatting address list when empty."""
    text = utils.format_address_management_text([])
    assert "[address_management_header]" in text
    assert "[no_addresses_message]" in text


def test_format_address_management_text_populated(mock_manager):
    """Test formatting address list with addresses."""
    addr = MagicMock(spec=DeliveryAddress)
    addr.address_label = "Home"
    addr.full_address = "123 St"

    text = utils.format_address_management_text([addr])

    assert "[address_management_header]" in text
    assert "Home" in text
    assert "123 St" in text


async def test_send_address_management_view_success(
    mock_manager, mock_user_service, mock_keyboards, mock_session
):
    """Test successfully sending the address management view."""
    message = AsyncMock()
    db_user = MagicMock(spec=User)
    db_user.id = 123

    mock_user_service.get_all_user_addresses = AsyncMock(return_value=[])

    await utils.send_address_management_view(message, mock_session, db_user)

    mock_user_service.get_all_user_addresses.assert_awaited_once_with(mock_session, 123)
    message.edit_text.assert_awaited_once()
    message.answer.assert_not_awaited()


async def test_send_address_management_view_not_modified(
    mock_manager, mock_user_service, mock_session
):
    """Test handling 'message is not modified' error."""
    message = AsyncMock()
    db_user = MagicMock(spec=User)

    mock_user_service.get_all_user_addresses = AsyncMock(return_value=[])
    message.edit_text.side_effect = TelegramBadRequest(
        method="edit", message="message is not modified"
    )

    await utils.send_address_management_view(message, mock_session, db_user)

    message.edit_text.assert_awaited_once()
    message.answer.assert_not_awaited()


async def test_send_address_management_view_fallback(
    mock_manager, mock_user_service, mock_session
):
    """Test fallback to answer() when edit_text fails with other error."""
    message = AsyncMock()
    db_user = MagicMock(spec=User)

    mock_user_service.get_all_user_addresses = AsyncMock(return_value=[])
    message.edit_text.side_effect = TelegramBadRequest(
        method="edit", message="Other error"
    )

    await utils.send_address_management_view(message, mock_session, db_user)

    message.edit_text.assert_awaited_once()
    message.answer.assert_awaited_once()


async def test_send_address_management_view_load_error(
    mock_manager, mock_user_service, mock_session
):
    """Test handling error during address loading."""
    message = AsyncMock()
    db_user = MagicMock(spec=User)

    mock_user_service.get_all_user_addresses.side_effect = Exception("DB Error")

    await utils.send_address_management_view(message, mock_session, db_user)

    message.answer.assert_awaited_once()
    # Should send error message
    args, _ = message.answer.call_args
    assert "[error_addresses_load_failed]" in args[0]
