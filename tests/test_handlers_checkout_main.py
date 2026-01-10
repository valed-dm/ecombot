"""
Unit tests for the main checkout handler.

This module verifies the logic for starting the checkout process, including:
- Handling empty carts.
- Determining whether to use the "fast path" (returning users) or "slow path"
  (new users).
"""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ecombot.bot.handlers.checkout import main
from ecombot.bot.handlers.checkout.states import CheckoutFSM
from ecombot.db.models import DeliveryAddress
from ecombot.db.models import User
from ecombot.schemas.dto import CartDTO


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager."""
    manager = mocker.patch("ecombot.bot.handlers.checkout.main.manager")
    manager.get_message.return_value = "Message text"
    return manager


@pytest.fixture
def mock_cart_service(mocker: MockerFixture):
    """Mocks the cart service."""
    return mocker.patch("ecombot.bot.handlers.checkout.main.cart_service")


@pytest.fixture
def mock_utils(mocker: MockerFixture):
    """Mocks the checkout utils and returns the mock objects for configuration."""
    return {
        "get_default_address": mocker.patch(
            "ecombot.bot.handlers.checkout.main.get_default_address"
        ),
        "determine_missing_info": mocker.patch(
            "ecombot.bot.handlers.checkout.main.determine_missing_info"
        ),
        "generate_fast_path": mocker.patch(
            "ecombot.bot.handlers.checkout.main.generate_fast_path_confirmation_text"
        ),
    }


@pytest.fixture
def mock_keyboards(mocker: MockerFixture):
    """Mocks the keyboard generator."""
    return mocker.patch(
        "ecombot.bot.handlers.checkout.main.get_fast_checkout_confirmation_keyboard"
    )


async def test_checkout_start_handler_empty_cart(
    mock_manager, mock_cart_service, mock_session
):
    """Test checkout start with an empty cart."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    db_user = MagicMock(spec=User)
    db_user.telegram_id = 123

    # Mock empty cart
    mock_cart = MagicMock(spec=CartDTO)
    mock_cart.items = []
    mock_cart_service.get_user_cart = AsyncMock(return_value=mock_cart)

    await main.checkout_start_handler(
        query, mock_session, db_user, state, callback_message
    )

    query.answer.assert_awaited_once()
    mock_cart_service.get_user_cart.assert_awaited_once_with(mock_session, 123)
    callback_message.answer.assert_awaited_once()
    # Should not set state
    state.set_state.assert_not_awaited()


async def test_checkout_start_handler_fast_path(
    mock_manager, mock_cart_service, mock_utils, mock_keyboards, mock_session
):
    """Test fast path checkout (user has phone and default address)."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()

    db_user = MagicMock(spec=User)
    db_user.telegram_id = 123
    db_user.phone = "1234567890"

    # Mock populated cart
    mock_cart = MagicMock(spec=CartDTO)
    mock_cart.items = [MagicMock()]
    mock_cart_service.get_user_cart = AsyncMock(return_value=mock_cart)

    # Mock default address found
    mock_address = MagicMock(spec=DeliveryAddress)
    mock_address.id = 1
    mock_utils["get_default_address"].return_value = mock_address
    mock_utils["generate_fast_path"].return_value = "Confirmation Text"

    await main.checkout_start_handler(
        query, mock_session, db_user, state, callback_message
    )

    state.update_data.assert_awaited_once_with(default_address_id=1)
    callback_message.answer.assert_awaited_once()
    state.set_state.assert_awaited_once_with(CheckoutFSM.confirm_fast_path)


async def test_checkout_start_handler_slow_path(
    mock_manager, mock_cart_service, mock_utils, mock_session
):
    """Test slow path checkout (missing info)."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()

    db_user = MagicMock(spec=User)
    db_user.telegram_id = 123
    db_user.phone = None  # Missing phone

    # Mock populated cart
    mock_cart = MagicMock(spec=CartDTO)
    mock_cart.items = [MagicMock()]
    mock_cart_service.get_user_cart = AsyncMock(return_value=mock_cart)

    # Mock missing info logic
    mock_utils["get_default_address"].return_value = None
    mock_utils["determine_missing_info"].return_value = ["phone", "address"]

    await main.checkout_start_handler(
        query, mock_session, db_user, state, callback_message
    )

    callback_message.answer.assert_awaited_once()
    state.set_state.assert_awaited_once_with(CheckoutFSM.getting_name)
