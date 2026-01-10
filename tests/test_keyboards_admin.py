"""
Unit tests for admin keyboards.

This module verifies:
- Generation of the main admin panel keyboard.
- Generation of order lists, filters, and detail view keyboards.
- Generation of the product edit menu keyboard.
"""

from unittest.mock import MagicMock

from aiogram.types import InlineKeyboardMarkup
import pytest
from pytest_mock import MockerFixture

from ecombot.bot.callback_data import AdminCallbackFactory
from ecombot.bot.callback_data import AdminNavCallbackFactory
from ecombot.bot.callback_data import EditProductCallbackFactory
from ecombot.bot.callback_data import OrderCallbackFactory
from ecombot.bot.keyboards import admin
from ecombot.schemas.dto import OrderDTO
from ecombot.schemas.enums import OrderStatus


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager to return predictable strings."""
    manager = mocker.patch("ecombot.bot.keyboards.admin.manager")
    # Return a string like "[key]" for any get_message call
    manager.get_message.side_effect = lambda section, key, **kwargs: f"[{key}]"
    return manager


def test_get_admin_panel_keyboard(mock_manager):
    """Test the main admin panel keyboard structure."""
    keyboard = admin.get_admin_panel_keyboard()
    assert isinstance(keyboard, InlineKeyboardMarkup)

    # Flatten buttons to check callback data
    buttons = [btn for row in keyboard.inline_keyboard for btn in row]
    callbacks = [btn.callback_data for btn in buttons]

    assert AdminCallbackFactory(action="add_category").pack() in callbacks
    assert AdminCallbackFactory(action="view_orders").pack() in callbacks
    assert AdminCallbackFactory(action="add_product").pack() in callbacks


def test_get_admin_orders_list_keyboard(mock_manager):
    """Test the orders list keyboard."""
    order1 = MagicMock(spec=OrderDTO)
    order1.id = 1
    order1.order_number = "ORD-001"
    order1.contact_name = "Alice"
    order1.total_price = 50.0

    keyboard = admin.get_admin_orders_list_keyboard([order1])

    buttons = [btn for row in keyboard.inline_keyboard for btn in row]
    callbacks = [btn.callback_data for btn in buttons]

    # Should have a button for the order and a back button
    assert OrderCallbackFactory(action="view_details", item_id=1).pack() in callbacks
    assert (
        AdminCallbackFactory(action="view_orders").pack() in callbacks
    )  # Back to filters


def test_get_admin_order_filters_keyboard(mock_manager):
    """Test the order filters keyboard."""
    keyboard = admin.get_admin_order_filters_keyboard()

    buttons = [btn for row in keyboard.inline_keyboard for btn in row]
    callbacks = [btn.callback_data for btn in buttons]

    assert "admin_order_filter:pending" in callbacks
    assert "admin_order_filter:completed" in callbacks
    assert AdminCallbackFactory(action="back_main").pack() in callbacks


def test_get_admin_order_details_keyboard_pending(mock_manager):
    """Test order details keyboard for PENDING status."""
    order = MagicMock(spec=OrderDTO)
    order.id = 10
    order.status = OrderStatus.PENDING

    keyboard = admin.get_admin_order_details_keyboard(order)
    callbacks = [btn.callback_data for row in keyboard.inline_keyboard for btn in row]

    # Should allow marking as processing and cancelling
    assert "admin_order_status:10:processing" in callbacks
    assert "admin_order_status:10:cancelled" in callbacks
    assert "admin_order_filter:pending" in callbacks  # Back button


def test_get_admin_order_details_keyboard_completed(mock_manager):
    """Test order details keyboard for COMPLETED status."""
    order = MagicMock(spec=OrderDTO)
    order.id = 10
    order.status = OrderStatus.COMPLETED

    keyboard = admin.get_admin_order_details_keyboard(order)
    callbacks = [btn.callback_data for row in keyboard.inline_keyboard for btn in row]

    # Should NOT allow cancelling or moving forward
    assert not any("admin_order_status" in cb for cb in callbacks)
    # Should only have back button
    assert "admin_order_filter:completed" in callbacks


def test_get_edit_product_menu_keyboard(mock_manager):
    """Test the product edit menu keyboard."""
    keyboard = admin.get_edit_product_menu_keyboard(
        product_id=5, product_list_message_id=100, category_id=2
    )
    callbacks = [btn.callback_data for row in keyboard.inline_keyboard for btn in row]

    # Check for edit fields
    assert EditProductCallbackFactory(action="name", product_id=5).pack() in callbacks
    assert EditProductCallbackFactory(action="price", product_id=5).pack() in callbacks
    assert (
        EditProductCallbackFactory(action="change_photo", product_id=5).pack()
        in callbacks
    )

    # Check navigation back button
    assert (
        AdminNavCallbackFactory(
            action="back_to_product_list", target_message_id=100, category_id=2
        ).pack()
        in callbacks
    )
