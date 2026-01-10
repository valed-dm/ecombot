"""
Unit tests for cart utilities.

This module verifies:
- Text formatting for the cart view.
- The logic for updating the cart message (handling edits and errors).
- The shared `alter_cart_item` logic used by management handlers.
"""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from aiogram.exceptions import TelegramBadRequest
import pytest
from pytest_mock import MockerFixture

from ecombot.bot.callback_data import CartCallbackFactory
from ecombot.bot.handlers.cart import utils
from ecombot.services.cart_service import CartItemNotFoundError


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager."""
    manager = mocker.patch("ecombot.bot.handlers.cart.utils.manager")
    manager.get_message.side_effect = lambda section, key, **kwargs: f"[{key}]"
    return manager


@pytest.fixture
def mock_cart_service(mocker: MockerFixture):
    """Mocks the cart service."""
    mock = mocker.patch("ecombot.bot.handlers.cart.utils.cart_service")
    mock.alter_item_quantity = AsyncMock()
    mock.get_user_cart = AsyncMock()
    return mock


@pytest.fixture
def mock_keyboards(mocker: MockerFixture):
    """Mocks the keyboard generator."""
    return mocker.patch("ecombot.bot.handlers.cart.utils.get_cart_keyboard")


def test_format_cart_text_empty(mock_manager):
    """Test formatting an empty cart."""
    cart_dto = MagicMock(items=[])
    text = utils.format_cart_text(cart_dto)
    assert "[cart_empty_message]" in text


def test_format_cart_text_populated(mock_manager):
    """Test formatting a cart with items."""
    item1 = MagicMock()
    item1.product.name = "P1"
    item1.product.price = 10.0
    item1.quantity = 2

    cart_dto = MagicMock(items=[item1], total_price=20.0)

    text = utils.format_cart_text(cart_dto)

    assert "[cart_header]" in text
    assert "[cart_item_template]" in text
    assert "[cart_total]" in text
    assert "<pre>" in text  # Ensure monospace block


async def test_update_cart_view_success(mock_keyboards):
    """Test successfully editing the cart message."""
    message = AsyncMock()
    cart_dto = MagicMock(items=[])

    result = await utils.update_cart_view(message, cart_dto)

    assert result is True
    message.edit_text.assert_awaited_once()


async def test_update_cart_view_not_modified(mock_keyboards):
    """Test handling 'message is not modified' error as success."""
    message = AsyncMock()
    message.edit_text.side_effect = TelegramBadRequest(
        method="edit", message="message is not modified"
    )
    cart_dto = MagicMock(items=[])

    result = await utils.update_cart_view(message, cart_dto)

    assert result is True
    message.edit_text.assert_awaited_once()


async def test_update_cart_view_error(mock_keyboards):
    """Test handling other edit errors as failure."""
    message = AsyncMock()
    message.edit_text.side_effect = TelegramBadRequest(
        method="edit", message="Other error"
    )
    cart_dto = MagicMock(items=[])

    result = await utils.update_cart_view(message, cart_dto)

    assert result is False
    message.edit_text.assert_awaited_once()


async def test_alter_cart_item_success(
    mock_manager, mock_cart_service, mock_session, mocker
):
    """Test successful item alteration."""
    query = AsyncMock()
    query.from_user.id = 123
    callback_data = CartCallbackFactory(action="increase", item_id=1)
    callback_message = AsyncMock()

    # Mock update_cart_view to return True
    mocker.patch("ecombot.bot.handlers.cart.utils.update_cart_view", return_value=True)

    await utils.alter_cart_item(
        query, callback_data, mock_session, callback_message, "increase"
    )

    mock_cart_service.alter_item_quantity.assert_awaited_once_with(
        mock_session, 123, 1, "increase"
    )
    query.answer.assert_awaited_once()
    assert "[success_quantity_increased]" in query.answer.call_args[0][0]


async def test_alter_cart_item_update_failed(
    mock_manager, mock_cart_service, mock_session, mocker
):
    """Test handling when view update fails."""
    query = AsyncMock()
    query.from_user.id = 123
    callback_data = CartCallbackFactory(action="increase", item_id=1)
    callback_message = AsyncMock()

    mocker.patch("ecombot.bot.handlers.cart.utils.update_cart_view", return_value=False)

    await utils.alter_cart_item(
        query, callback_data, mock_session, callback_message, "increase"
    )

    query.answer.assert_awaited_once()
    assert "[error_cart_update_failed]" in query.answer.call_args[0][0]


async def test_alter_cart_item_not_found(
    mock_manager, mock_cart_service, mock_session, mocker
):
    """Test handling CartItemNotFoundError (refresh cart)."""
    query = AsyncMock()
    query.from_user.id = 123
    callback_data = CartCallbackFactory(action="increase", item_id=1)
    callback_message = AsyncMock()

    mock_cart_service.alter_item_quantity.side_effect = CartItemNotFoundError()
    mock_update_view = mocker.patch(
        "ecombot.bot.handlers.cart.utils.update_cart_view", return_value=True
    )

    await utils.alter_cart_item(
        query, callback_data, mock_session, callback_message, "increase"
    )

    # Should fetch fresh cart and update view
    mock_cart_service.get_user_cart.assert_awaited_once_with(mock_session, 123)
    mock_update_view.assert_awaited_once()
    query.answer.assert_awaited_once()
    assert "[error_cart_item_not_found]" in query.answer.call_args[0][0]
