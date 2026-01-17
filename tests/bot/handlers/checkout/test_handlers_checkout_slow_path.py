"""
Unit tests for slow path checkout handlers.

This module verifies:
- Collecting user details (name, phone, address).
- Final confirmation and order placement (saving details + creating order).
- Cancellation logic.
"""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from aiogram.fsm.context import FSMContext
from aiogram.types import Contact
import pytest
from pytest_mock import MockerFixture

from ecombot.bot.handlers.checkout import slow_path
from ecombot.bot.handlers.checkout.states import CheckoutFSM
from ecombot.db.models import DeliveryAddress
from ecombot.db.models import User
from ecombot.services.order_service import OrderPlacementError


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager."""
    manager = mocker.patch("ecombot.bot.handlers.checkout.slow_path.manager")
    manager.get_message.return_value = "Message text"
    return manager


@pytest.fixture
def mock_cart_service(mocker: MockerFixture):
    """Mocks the cart service."""
    return mocker.patch("ecombot.bot.handlers.checkout.slow_path.cart_service")


@pytest.fixture
def mock_user_service(mocker: MockerFixture):
    """Mocks the user service."""
    return mocker.patch("ecombot.bot.handlers.checkout.slow_path.user_service")


@pytest.fixture
def mock_order_service(mocker: MockerFixture):
    """Mocks the order service."""
    mock = mocker.patch("ecombot.bot.handlers.checkout.slow_path.order_service")
    mock.place_order = AsyncMock()
    return mock


@pytest.fixture
def mock_notification_service(mocker: MockerFixture):
    """Mocks the notification service."""
    mock = mocker.patch("ecombot.bot.handlers.checkout.slow_path.notification_service")
    mock.notify_admins_new_order = AsyncMock()
    return mock


@pytest.fixture
def mock_utils(mocker: MockerFixture):
    """Mocks utility functions."""
    return mocker.patch(
        "ecombot.bot.handlers.checkout.slow_path.generate_slow_path_confirmation_text",
        return_value="Confirmation Text",
    )


@pytest.fixture
def mock_keyboards(mocker: MockerFixture):
    """Mocks keyboard generators."""
    mocker.patch("ecombot.bot.handlers.checkout.slow_path.get_request_contact_keyboard")
    mocker.patch(
        "ecombot.bot.handlers.checkout.slow_path.get_checkout_confirmation_keyboard"
    )
    mocker.patch("ecombot.bot.handlers.checkout.slow_path.ReplyKeyboardRemove")


async def test_get_name_handler(mock_manager, mock_keyboards):
    """Test receiving name and asking for phone."""
    message = AsyncMock()
    message.text = "John Doe"
    state = AsyncMock(spec=FSMContext)

    await slow_path.get_name_handler(message, state)

    state.update_data.assert_awaited_once_with(name="John Doe")
    message.answer.assert_awaited_once()
    state.set_state.assert_awaited_once_with(CheckoutFSM.getting_phone)


async def test_get_phone_handler_text(
    mock_manager, mock_keyboards, mock_session, mocker
):
    """Test receiving phone as text."""
    mocker.patch(
        "ecombot.bot.handlers.checkout.slow_path.check_courier_availability",
        return_value=True,
        new_callable=AsyncMock,
    )
    message = AsyncMock()
    message.text = "1234567890"
    message.contact = None
    state = AsyncMock(spec=FSMContext)
    db_user = MagicMock(spec=User)

    await slow_path.get_phone_handler(message, mock_session, state, db_user)

    state.update_data.assert_any_call(phone="1234567890")
    state.update_data.assert_any_call(is_pickup=False)
    message.answer.assert_awaited_once()
    state.set_state.assert_awaited_once_with(CheckoutFSM.getting_address)


async def test_get_phone_handler_contact(
    mock_manager, mock_keyboards, mock_session, mocker
):
    """Test receiving phone as contact."""
    mocker.patch(
        "ecombot.bot.handlers.checkout.slow_path.check_courier_availability",
        return_value=True,
        new_callable=AsyncMock,
    )
    message = AsyncMock()
    message.text = None
    contact = MagicMock(spec=Contact)
    contact.phone_number = "9876543210"
    message.contact = contact
    state = AsyncMock(spec=FSMContext)
    db_user = MagicMock(spec=User)

    await slow_path.get_phone_handler(message, mock_session, state, db_user)

    state.update_data.assert_any_call(phone="9876543210")
    state.update_data.assert_any_call(is_pickup=False)
    message.answer.assert_awaited_once()
    state.set_state.assert_awaited_once_with(CheckoutFSM.getting_address)


async def test_get_phone_handler_invalid(mock_manager, mock_session):
    """Test receiving invalid phone input."""
    message = AsyncMock()
    message.text = None
    message.contact = None
    state = AsyncMock(spec=FSMContext)
    db_user = MagicMock(spec=User)

    await slow_path.get_phone_handler(message, mock_session, state, db_user)

    message.answer.assert_awaited_once()  # Error message
    state.update_data.assert_not_awaited()
    state.set_state.assert_not_awaited()


async def test_get_address_handler_success(
    mock_manager, mock_cart_service, mock_utils, mock_keyboards, mock_session
):
    """Test receiving address and showing confirmation."""
    message = AsyncMock()
    message.text = "123 Main St"
    state = AsyncMock(spec=FSMContext)
    db_user = MagicMock(spec=User)
    db_user.telegram_id = 123

    state.get_data.return_value = {"name": "John", "phone": "123"}
    mock_cart_service.get_user_cart = AsyncMock(return_value=MagicMock())

    await slow_path.get_address_handler(message, mock_session, state, db_user)

    state.update_data.assert_awaited_once_with(address="123 Main St")
    mock_cart_service.get_user_cart.assert_awaited_once_with(mock_session, 123)
    message.answer.assert_awaited_once()
    state.set_state.assert_awaited_once_with(CheckoutFSM.confirm_slow_path)


async def test_get_address_handler_invalid(mock_manager, mock_session):
    """Test receiving invalid address."""
    message = AsyncMock()
    message.text = "   "
    state = AsyncMock(spec=FSMContext)
    db_user = MagicMock(spec=User)

    await slow_path.get_address_handler(message, mock_session, state, db_user)

    message.answer.assert_awaited_once()  # Error message
    state.update_data.assert_not_awaited()


async def test_slow_path_confirm_handler_success(
    mock_manager,
    mock_user_service,
    mock_order_service,
    mock_notification_service,
    mock_session,
    mocker,
):
    """Test confirming order in slow path."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock(spec=FSMContext)
    db_user = MagicMock(spec=User)
    db_user.id = 1

    state.get_data.return_value = {"phone": "123", "address": "Street", "is_pickup": False}

    # Mock user service calls
    mock_user_service.update_profile_details = AsyncMock()
    mock_address = MagicMock(spec=DeliveryAddress)
    mock_address.id = 10
    mock_user_service.add_new_address = AsyncMock(return_value=mock_address)
    mock_user_service.set_user_default_address = AsyncMock()

    # Mock session.get to return user for refresh
    mock_session.get.return_value = db_user

    # Mock order placement
    mock_dto = MagicMock()
    mock_dto.display_order_number = "ORD-1"
    mock_order_service.place_order.return_value = mock_dto

    await slow_path.slow_path_confirm_handler(
        query, mock_session, db_user, state, callback_message
    )

    # Verify flow
    mock_user_service.update_profile_details.assert_awaited_once()
    mock_user_service.add_new_address.assert_awaited_once()
    mock_user_service.set_user_default_address.assert_awaited_once()
    mock_order_service.place_order.assert_awaited_once()
    mock_notification_service.notify_admins_new_order.assert_awaited_once()

    assert callback_message.edit_text.await_count == 2  # Progress -> Success
    state.clear.assert_awaited_once()
    query.answer.assert_awaited_once()


async def test_slow_path_confirm_handler_placement_error(
    mock_manager, mock_user_service, mock_order_service, mock_session, mocker
):
    """Test handling order placement error."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock(spec=FSMContext)
    db_user = MagicMock(spec=User)
    db_user.id = 1

    state.get_data.return_value = {"phone": "123", "address": "Street", "is_pickup": False}

    # Setup mocks to pass until place_order
    mock_user_service.add_new_address = AsyncMock(return_value=MagicMock(id=1))
    mock_user_service.update_profile_details = AsyncMock()
    mock_user_service.set_user_default_address = AsyncMock()
    mock_session.get.return_value = db_user

    mock_order_service.place_order.side_effect = OrderPlacementError("Stock issue")

    await slow_path.slow_path_confirm_handler(
        query, mock_session, db_user, state, callback_message
    )

    assert callback_message.edit_text.await_count == 2  # Progress -> Error
    state.clear.assert_awaited_once()


async def test_slow_path_cancel_handler(mock_manager):
    """Test cancelling slow path checkout."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock(spec=FSMContext)

    await slow_path.slow_path_cancel_handler(query, state, callback_message)

    callback_message.edit_text.assert_awaited_once()
    state.clear.assert_awaited_once()
    query.answer.assert_awaited_once()
