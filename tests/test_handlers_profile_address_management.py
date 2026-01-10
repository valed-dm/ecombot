"""
Unit tests for profile address management handlers.

This module verifies:
- Viewing specific address details.
- Managing addresses (listing).
- Deleting and setting default addresses.
- The 'Add Address' FSM flow.
"""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from aiogram.fsm.context import FSMContext
import pytest
from pytest_mock import MockerFixture

from ecombot.bot.callback_data import ProfileCallbackFactory
from ecombot.bot.handlers.profile import address_management
from ecombot.bot.handlers.profile.states import AddAddress
from ecombot.db.models import DeliveryAddress
from ecombot.db.models import User


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager."""
    manager = mocker.patch("ecombot.bot.handlers.profile.address_management.manager")
    manager.get_message.return_value = "Message text"
    return manager


@pytest.fixture
def mock_user_service(mocker: MockerFixture):
    """Mocks the user service."""
    return mocker.patch("ecombot.bot.handlers.profile.address_management.user_service")


@pytest.fixture
def mock_send_view(mocker: MockerFixture):
    """Mocks the send_address_management_view helper."""
    return mocker.patch(
        "ecombot.bot.handlers.profile.address_management.send_address_management_view",
        new_callable=AsyncMock,
    )


@pytest.fixture
def mock_keyboards(mocker: MockerFixture):
    """Mocks keyboard generators."""
    mocker.patch(
        "ecombot.bot.handlers.profile.address_management.get_address_details_keyboard"
    )
    mocker.patch("ecombot.bot.handlers.profile.address_management.get_cancel_keyboard")


async def test_view_address_handler_success(
    mock_manager, mock_user_service, mock_keyboards, mock_session
):
    """Test viewing a specific address."""
    query = AsyncMock()
    callback_message = AsyncMock()
    db_user = MagicMock(spec=User)
    db_user.id = 123
    callback_data = ProfileCallbackFactory(action="view_addr", address_id=10)

    mock_addr = MagicMock(spec=DeliveryAddress)
    mock_addr.id = 10
    mock_addr.is_default = True
    mock_addr.address_label = "Home"
    mock_addr.full_address = "123 St"

    mock_user_service.get_all_user_addresses = AsyncMock(return_value=[mock_addr])

    await address_management.view_address_handler(
        query, callback_data, mock_session, db_user, callback_message
    )

    callback_message.edit_text.assert_awaited_once()
    query.answer.assert_awaited_once()


async def test_view_address_handler_not_found(
    mock_manager, mock_user_service, mock_session
):
    """Test viewing an address that doesn't exist."""
    query = AsyncMock()
    callback_message = AsyncMock()
    db_user = MagicMock(spec=User)
    db_user.id = 123
    callback_data = ProfileCallbackFactory(action="view_addr", address_id=999)

    mock_user_service.get_all_user_addresses = AsyncMock(return_value=[])

    await address_management.view_address_handler(
        query, callback_data, mock_session, db_user, callback_message
    )

    callback_message.edit_text.assert_not_awaited()
    query.answer.assert_awaited_once()
    assert query.answer.call_args[1].get("show_alert") is True


async def test_manage_addresses_handler(mock_send_view, mock_session):
    """Test the manage addresses entry point."""
    query = AsyncMock()
    callback_message = AsyncMock()
    db_user = MagicMock(spec=User)

    await address_management.manage_addresses_handler(
        query, mock_session, db_user, callback_message
    )

    mock_send_view.assert_awaited_once_with(callback_message, mock_session, db_user)
    query.answer.assert_awaited_once()


async def test_delete_address_handler_success(
    mock_manager, mock_user_service, mock_send_view, mock_session
):
    """Test successful address deletion."""
    query = AsyncMock()
    callback_message = AsyncMock()
    db_user = MagicMock(spec=User)
    db_user.id = 123
    callback_data = ProfileCallbackFactory(action="delete_addr", address_id=10)

    mock_user_service.delete_address = AsyncMock()

    await address_management.delete_address_handler(
        query, callback_data, mock_session, db_user, callback_message
    )

    mock_user_service.delete_address.assert_awaited_once_with(mock_session, 123, 10)
    query.answer.assert_awaited_once()
    assert query.answer.call_args[1].get("show_alert") is True
    mock_send_view.assert_awaited_once_with(callback_message, mock_session, db_user)


async def test_set_default_address_handler_success(
    mock_manager, mock_user_service, mock_send_view, mock_session
):
    """Test setting default address."""
    query = AsyncMock()
    callback_message = AsyncMock()
    db_user = MagicMock(spec=User)
    db_user.id = 123
    callback_data = ProfileCallbackFactory(action="set_default_addr", address_id=10)

    mock_user_service.set_user_default_address = AsyncMock()

    await address_management.set_default_address_handler(
        query, callback_data, mock_session, db_user, callback_message
    )

    mock_user_service.set_user_default_address.assert_awaited_once_with(
        mock_session, 123, 10
    )
    query.answer.assert_awaited_once()
    assert query.answer.call_args[1].get("show_alert") is False
    mock_send_view.assert_awaited_once_with(callback_message, mock_session, db_user)


async def test_add_address_start(mock_manager, mock_keyboards):
    """Test starting add address flow."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock(spec=FSMContext)

    await address_management.add_address_start(query, state, callback_message)

    callback_message.edit_text.assert_awaited_once()
    state.set_state.assert_awaited_once_with(AddAddress.getting_label)
    query.answer.assert_awaited_once()


async def test_add_address_get_label(mock_manager, mock_keyboards):
    """Test receiving address label."""
    message = AsyncMock()
    message.text = "Home"
    state = AsyncMock(spec=FSMContext)

    await address_management.add_address_get_label(message, state)

    state.update_data.assert_awaited_once_with(label="Home")
    state.set_state.assert_awaited_once_with(AddAddress.getting_address)
    message.answer.assert_awaited_once()


async def test_add_address_get_address_success(
    mock_manager, mock_user_service, mock_send_view, mock_session
):
    """Test receiving full address and saving."""
    message = AsyncMock()
    message.text = "123 Main St"
    state = AsyncMock(spec=FSMContext)
    db_user = MagicMock(spec=User)
    db_user.id = 123

    state.get_data.return_value = {"label": "Home", "address": "123 Main St"}
    mock_user_service.add_new_address = AsyncMock()

    await address_management.add_address_get_address(
        message, state, mock_session, db_user
    )

    state.update_data.assert_awaited_once_with(address="123 Main St")
    mock_user_service.add_new_address.assert_awaited_once_with(
        session=mock_session, user_id=123, label="Home", address="123 Main St"
    )
    message.answer.assert_awaited_once()
    mock_send_view.assert_awaited_once_with(message, mock_session, db_user)
    state.clear.assert_awaited_once()
