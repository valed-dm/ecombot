"""
Unit tests for cart keyboards.

This module verifies:
- Generation of the cart keyboard for empty and populated carts.
- Presence of item management buttons (increase, decrease, remove).
- Presence of navigation buttons (checkout, catalog).
"""

from unittest.mock import MagicMock

from aiogram.types import InlineKeyboardMarkup
import pytest
from pytest_mock import MockerFixture

from ecombot.bot.callback_data import CartCallbackFactory
from ecombot.bot.callback_data import CatalogCallbackFactory
from ecombot.bot.keyboards import cart as cart_keyboards
from ecombot.schemas.dto import CartDTO


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager to return predictable strings."""
    manager = mocker.patch("ecombot.bot.keyboards.cart.manager")
    manager.get_message.side_effect = lambda section, key, **kwargs: f"[{key}]"
    return manager


def test_get_cart_keyboard_empty(mock_manager):
    """Test cart keyboard when cart is empty."""
    cart_dto = MagicMock(spec=CartDTO)
    cart_dto.items = []

    keyboard = cart_keyboards.get_cart_keyboard(cart_dto)

    assert isinstance(keyboard, InlineKeyboardMarkup)

    # Flatten buttons
    buttons = [btn for row in keyboard.inline_keyboard for btn in row]
    callbacks = [btn.callback_data for btn in buttons]

    # Should have Catalog button
    assert CatalogCallbackFactory(action="back_to_main", item_id=0).pack() in callbacks

    # Should NOT have checkout button
    assert "checkout_start" not in callbacks


def test_get_cart_keyboard_populated(mock_manager):
    """Test cart keyboard with items."""
    item1 = MagicMock()
    item1.id = 10
    item1.quantity = 2
    item1.product.id = 100
    item1.product.name = "Test Product"

    cart_dto = MagicMock(spec=CartDTO)
    cart_dto.items = [item1]

    keyboard = cart_keyboards.get_cart_keyboard(cart_dto)

    buttons = [btn for row in keyboard.inline_keyboard for btn in row]
    callbacks = [btn.callback_data for btn in buttons]
    texts = [btn.text for btn in buttons]

    # Check item actions
    assert CartCallbackFactory(action="decrease", item_id=10).pack() in callbacks
    assert CartCallbackFactory(action="increase", item_id=10).pack() in callbacks
    assert CartCallbackFactory(action="remove", item_id=10).pack() in callbacks

    # Check product link
    assert (
        CatalogCallbackFactory(action="view_product", item_id=100).pack() in callbacks
    )

    # Check static quantity button (dummy callback)
    assert "quantity_10" in callbacks
    assert "2" in texts

    # Check checkout and catalog
    assert "checkout_start" in callbacks
    assert CatalogCallbackFactory(action="back_to_main", item_id=0).pack() in callbacks
