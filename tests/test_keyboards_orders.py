"""
Unit tests for order keyboards.

This module verifies:
- Generation of the orders list keyboard (empty vs populated).
- Generation of the order details keyboard (back navigation).
"""

from unittest.mock import MagicMock

from aiogram.types import InlineKeyboardMarkup
import pytest
from pytest_mock import MockerFixture

from ecombot.bot.callback_data import CatalogCallbackFactory
from ecombot.bot.callback_data import OrderCallbackFactory
from ecombot.bot.keyboards import orders
from ecombot.schemas.dto import OrderDTO


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager to return predictable strings."""
    manager = mocker.patch("ecombot.bot.keyboards.orders.manager")
    manager.get_message.side_effect = lambda section, key, **kwargs: f"[{key}]"
    return manager


def test_get_orders_list_keyboard_empty(mock_manager):
    """Test orders list keyboard when user has no orders."""
    keyboard = orders.get_orders_list_keyboard([])
    assert isinstance(keyboard, InlineKeyboardMarkup)

    buttons = [btn for row in keyboard.inline_keyboard for btn in row]
    callbacks = [btn.callback_data for btn in buttons]
    texts = [btn.text for btn in buttons]

    assert "[go_to_catalog]" in texts
    assert CatalogCallbackFactory(action="back_to_main", item_id=0).pack() in callbacks


def test_get_orders_list_keyboard_populated(mock_manager):
    """Test orders list keyboard with orders."""
    order1 = MagicMock(spec=OrderDTO)
    order1.id = 10
    order1.order_number = "ORD-10"

    order2 = MagicMock(spec=OrderDTO)
    order2.id = 11
    order2.order_number = "ORD-11"

    keyboard = orders.get_orders_list_keyboard([order1, order2])

    buttons = [btn for row in keyboard.inline_keyboard for btn in row]
    callbacks = [btn.callback_data for btn in buttons]

    assert OrderCallbackFactory(action="view_details", item_id=10).pack() in callbacks
    assert OrderCallbackFactory(action="view_details", item_id=11).pack() in callbacks


def test_get_order_details_keyboard(mock_manager):
    """Test the order details keyboard."""
    keyboard = orders.get_order_details_keyboard()
    assert isinstance(keyboard, InlineKeyboardMarkup)

    buttons = [btn for row in keyboard.inline_keyboard for btn in row]
    callbacks = [btn.callback_data for btn in buttons]
    texts = [btn.text for btn in buttons]

    assert "[back_to_orders]" in texts
    assert OrderCallbackFactory(action="back_to_list").pack() in callbacks
