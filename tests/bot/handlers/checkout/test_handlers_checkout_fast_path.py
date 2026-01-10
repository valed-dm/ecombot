"""
Unit tests for fast path checkout handlers.

This module verifies:
- Order confirmation (success, address not found, placement error, generic error).
- Cancellation of the checkout process.
- Redirection to profile editing.
"""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ecombot.bot.handlers.checkout import fast_path
from ecombot.db.models import DeliveryAddress
from ecombot.db.models import Order
from ecombot.db.models import User
from ecombot.services.order_service import OrderPlacementError


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager."""
    manager = mocker.patch("ecombot.bot.handlers.checkout.fast_path.manager")
    manager.get_message.return_value = "Message text"
    return manager


@pytest.fixture
def mock_order_service(mocker: MockerFixture):
    """Mocks the order service."""
    mock = mocker.patch("ecombot.bot.handlers.checkout.fast_path.order_service")
    mock.place_order = AsyncMock()
    return mock


async def test_fast_checkout_confirm_handler_success(
    mock_manager, mock_order_service, mock_session
):
    """Test successful order placement via fast path."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    db_user = MagicMock(spec=User)
    db_user.id = 123

    # Mock state data
    state.get_data.return_value = {"default_address_id": 1}

    # Mock DB address retrieval
    mock_address = MagicMock(spec=DeliveryAddress)
    mock_session.get.return_value = mock_address

    # Mock order placement
    mock_order = MagicMock(spec=Order)
    mock_order.order_number = "ORD-123"
    mock_order_service.place_order = AsyncMock(return_value=mock_order)

    await fast_path.fast_checkout_confirm_handler(
        query, mock_session, db_user, state, callback_message
    )

    # Verify progress message
    assert callback_message.edit_text.await_count == 2
    # Verify order placement call
    mock_order_service.place_order.assert_awaited_once_with(
        session=mock_session, db_user=db_user, delivery_address=mock_address
    )
    # Verify cleanup
    state.clear.assert_awaited_once()
    query.answer.assert_awaited_once()


async def test_fast_checkout_confirm_handler_address_not_found(
    mock_manager, mock_order_service, mock_session
):
    """Test handling when the default address is missing."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    db_user = MagicMock(spec=User)

    state.get_data.return_value = {"default_address_id": 1}
    mock_session.get.return_value = None  # Address not found

    await fast_path.fast_checkout_confirm_handler(
        query, mock_session, db_user, state, callback_message
    )

    mock_order_service.place_order.assert_not_awaited()
    assert callback_message.edit_text.await_count == 2
    state.clear.assert_awaited_once()


async def test_fast_checkout_confirm_handler_placement_error(
    mock_manager, mock_order_service, mock_session
):
    """Test handling of OrderPlacementError (e.g., stock issues)."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    db_user = MagicMock(spec=User)

    state.get_data.return_value = {"default_address_id": 1}
    mock_session.get.return_value = MagicMock(spec=DeliveryAddress)

    mock_order_service.place_order.side_effect = OrderPlacementError("Stock error")

    await fast_path.fast_checkout_confirm_handler(
        query, mock_session, db_user, state, callback_message
    )

    # Should edit text twice (progress -> error)
    assert callback_message.edit_text.await_count == 2
    state.clear.assert_awaited_once()


async def test_fast_checkout_confirm_handler_generic_error(
    mock_manager, mock_order_service, mock_session
):
    """Test handling of unexpected exceptions."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    db_user = MagicMock(spec=User)
    db_user.id = 123

    state.get_data.return_value = {"default_address_id": 1}
    mock_session.get.return_value = MagicMock(spec=DeliveryAddress)

    mock_order_service.place_order.side_effect = Exception("Boom")

    await fast_path.fast_checkout_confirm_handler(
        query, mock_session, db_user, state, callback_message
    )

    assert callback_message.edit_text.await_count == 2
    state.clear.assert_awaited_once()


async def test_fast_checkout_cancel_handler(mock_manager):
    """Test cancellation handler."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()

    await fast_path.fast_checkout_cancel_handler(query, state, callback_message)

    callback_message.edit_text.assert_awaited_once()
    state.clear.assert_awaited_once()
    query.answer.assert_awaited_once()


async def test_fast_checkout_edit_handler(mock_manager, mock_session, mocker):
    """Test redirection to profile editing."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    db_user = MagicMock(spec=User)

    # Mock the profile handler which is imported inside the function
    mock_profile_handler = mocker.patch(
        "ecombot.bot.handlers.profile.profile_handler", new_callable=AsyncMock
    )

    # Mock callback_message.answer to return a new message object
    new_message = AsyncMock()
    callback_message.answer.return_value = new_message

    await fast_path.fast_checkout_edit_handler(
        query, state, callback_message, mock_session, db_user
    )

    state.clear.assert_awaited_once()
    callback_message.answer.assert_awaited_once()
    mock_profile_handler.assert_awaited_once_with(new_message, mock_session, db_user)
    callback_message.delete.assert_awaited_once()
    query.answer.assert_awaited_once()
