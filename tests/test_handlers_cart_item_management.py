"""
Unit tests for cart item management handlers.

This module verifies that the handlers for increasing, decreasing, and removing
cart items correctly delegate to the `alter_cart_item` utility function with
the appropriate action.
"""

from unittest.mock import AsyncMock

import pytest
from pytest_mock import MockerFixture

from ecombot.bot.callback_data import CartCallbackFactory


@pytest.fixture
def handlers():
    """Import the module under test inside a fixture to avoid collection errors."""
    from ecombot.bot.handlers.cart import item_management

    return item_management


@pytest.fixture
def mock_alter_cart_item(mocker: MockerFixture):
    """Mocks the shared utility function."""
    return mocker.patch(
        "ecombot.bot.handlers.cart.item_management.alter_cart_item",
        new_callable=AsyncMock,
    )


async def test_decrease_cart_item_handler(handlers, mock_alter_cart_item, mock_session):
    """Test decreasing item quantity."""
    query = AsyncMock()
    callback_data = CartCallbackFactory(action="decrease", item_id=1)
    callback_message = AsyncMock()

    await handlers.decrease_cart_item_handler(
        query, callback_data, mock_session, callback_message
    )

    mock_alter_cart_item.assert_awaited_once_with(
        query, callback_data, mock_session, callback_message, action="decrease"
    )


async def test_increase_cart_item_handler(handlers, mock_alter_cart_item, mock_session):
    """Test increasing item quantity."""
    query = AsyncMock()
    callback_data = CartCallbackFactory(action="increase", item_id=1)
    callback_message = AsyncMock()

    await handlers.increase_cart_item_handler(
        query, callback_data, mock_session, callback_message
    )

    mock_alter_cart_item.assert_awaited_once_with(
        query, callback_data, mock_session, callback_message, action="increase"
    )


async def test_remove_cart_item_handler(handlers, mock_alter_cart_item, mock_session):
    """Test removing an item."""
    query = AsyncMock()
    callback_data = CartCallbackFactory(action="remove", item_id=1)
    callback_message = AsyncMock()

    await handlers.remove_cart_item_handler(
        query, callback_data, mock_session, callback_message
    )

    mock_alter_cart_item.assert_awaited_once_with(
        query, callback_data, mock_session, callback_message, action="remove"
    )
