"""
Unit tests for cart viewing handlers.

This module verifies:
- The /cart command handler (fetching cart, formatting text, sending message).
- The 'Add to Cart' callback handler (success, error handling for stock/not found).
"""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ecombot.bot.callback_data import CartCallbackFactory
from ecombot.bot.handlers.cart import viewing
from ecombot.services.cart_service import ProductNotFoundError


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager."""
    return mocker.patch("ecombot.bot.handlers.cart.viewing.manager")


@pytest.fixture
def mock_cart_service(mocker: MockerFixture):
    """Mocks the cart service."""
    mock = mocker.patch("ecombot.bot.handlers.cart.viewing.cart_service")
    mock.get_user_cart = AsyncMock()
    mock.add_product_to_cart = AsyncMock()
    return mock


@pytest.fixture
def mock_utils(mocker: MockerFixture):
    """Mocks the cart utils."""
    return mocker.patch("ecombot.bot.handlers.cart.viewing.format_cart_text")


@pytest.fixture
def mock_keyboards(mocker: MockerFixture):
    """Mocks the keyboard generator."""
    return mocker.patch("ecombot.bot.handlers.cart.viewing.get_cart_keyboard")


async def test_view_cart_handler_success(
    mock_manager, mock_cart_service, mock_utils, mock_keyboards, mock_session
):
    """Test displaying the cart."""
    message = AsyncMock()
    message.from_user.id = 123

    mock_cart_dto = MagicMock()
    mock_cart_service.get_user_cart = AsyncMock(return_value=mock_cart_dto)
    mock_utils.return_value = "Cart Text"

    await viewing.view_cart_handler(message, mock_session)

    mock_cart_service.get_user_cart.assert_awaited_once_with(mock_session, 123)
    mock_utils.assert_called_once_with(mock_cart_dto)
    message.answer.assert_awaited_once()


async def test_add_to_cart_handler_success(
    mock_manager, mock_cart_service, mock_session
):
    """Test successfully adding an item to the cart."""
    query = AsyncMock()
    query.from_user.id = 123
    callback_data = CartCallbackFactory(action="add", item_id=10)

    await viewing.add_to_cart_handler(query, callback_data, mock_session)

    mock_cart_service.add_product_to_cart.assert_awaited_once_with(
        session=mock_session, user_id=123, product_id=10
    )
    query.answer.assert_awaited_once()
    # Should be a success message (not alert)
    assert query.answer.call_args[1].get("show_alert") is False


async def test_add_to_cart_handler_product_not_found(
    mock_manager, mock_cart_service, mock_session
):
    """Test handling product not found error."""
    query = AsyncMock()
    query.from_user.id = 123
    callback_data = CartCallbackFactory(action="add", item_id=10)

    mock_cart_service.add_product_to_cart.side_effect = ProductNotFoundError(
        "Not found"
    )

    await viewing.add_to_cart_handler(query, callback_data, mock_session)

    query.answer.assert_awaited_once_with("Not found", show_alert=True)


async def test_add_to_cart_handler_generic_error(
    mock_manager, mock_cart_service, mock_session
):
    """Test handling generic errors."""
    query = AsyncMock()
    query.from_user.id = 123
    callback_data = CartCallbackFactory(action="add", item_id=10)

    mock_cart_service.add_product_to_cart.side_effect = Exception("Boom")

    await viewing.add_to_cart_handler(query, callback_data, mock_session)

    query.answer.assert_awaited_once()
    assert query.answer.call_args[1].get("show_alert") is True
