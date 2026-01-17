"""
Unit tests for admin order utilities.

This module verifies:
- Text generation for order details (standard, deleted items, truncation).
- Sending/editing the order details view with fallback logic.
"""

from datetime import datetime
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ecombot.bot.handlers.admin.orders import utils
from ecombot.schemas.enums import OrderStatus


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager."""
    return mocker.patch("ecombot.bot.handlers.admin_orders.utils.manager")


@pytest.fixture
def mock_keyboards(mocker: MockerFixture):
    """Mocks the keyboard generator."""
    return mocker.patch(
        "ecombot.bot.handlers.admin_orders.utils.get_admin_order_details_keyboard"
    )


def setup_mock_manager_responses(mock_manager):
    """Helper to configure manager.get_message side effects."""

    def side_effect(section, key, **kwargs):
        if key == "max_message_length":
            return "100"  # Small limit for testing truncation
        if key == "truncate_threshold":
            return "50"
        if key == "not_available":
            return "N/A"
        # Return a predictable string for other keys
        return f"[{key}]"

    mock_manager.get_message.side_effect = side_effect


def test_generate_order_details_text_standard(mock_manager):
    """Test generating text for a standard order."""
    # Setup manager to return large limits to avoid truncation
    mock_manager.get_message.side_effect = lambda s, k, **kw: (
        "4096"
        if k == "max_message_length"
        else "4000" if k == "truncate_threshold" else f"[{k}]"
    )

    # Mock OrderDTO
    order = MagicMock()
    order.order_number = "ORD-123"
    order.status = OrderStatus.PENDING
    order.created_at = datetime(2023, 1, 1, 12, 0)
    order.contact_name = "John Doe"
    order.phone = "12345"
    order.address = "Main St"

    # Mock Item
    item = MagicMock()
    item.product.name = "Widget"
    item.product.deleted_at = None  # Active product
    item.quantity = 2
    item.price = 10.0
    order.items = [item]

    text = utils.generate_order_details_text(order)

    assert "[order_details_header]" in text
    assert "[order_status_field]" in text
    assert "[customer_info_header]" in text
    assert "[item_template]" in text
    assert "[order_total]" in text
    # Should NOT contain deleted items logic
    assert "[deleted_items_notice]" not in text


def test_generate_order_details_text_with_deleted_items(mock_manager):
    """Test generating text when order contains soft-deleted products."""

    def side_effect(section, key, **kwargs):
        if key == "max_message_length":
            return "4096"
        if key == "truncate_threshold":
            return "4000"
        if key == "item_template":
            return f"[{key}]{kwargs.get('status', '')}"
        return f"[{key}]"

    mock_manager.get_message.side_effect = side_effect

    order = MagicMock()
    order.order_number = "ORD-123"
    order.status = OrderStatus.PAID
    order.created_at = datetime.now()
    order.contact_name = "Jane Doe"
    order.phone = None  # Test N/A fallback
    order.address = None

    # Active Item
    item1 = MagicMock()
    item1.product.name = "P1"
    item1.product.deleted_at = None
    item1.price = 10.0
    item1.quantity = 1

    # Deleted Item
    item2 = MagicMock()
    item2.product.name = "P2"
    item2.product.deleted_at = datetime.now()
    item2.price = 20.0
    item2.quantity = 1

    order.items = [item1, item2]

    text = utils.generate_order_details_text(order)

    assert "[deleted_product_suffix]" in text  # Called for item2
    assert "[active_items_total]" in text
    assert "[deleted_items_total]" in text
    assert "[final_total]" in text
    assert "[deleted_items_notice]" in text


def test_generate_order_details_text_truncation(mock_manager):
    """Test that text is truncated if it exceeds limits."""
    setup_mock_manager_responses(mock_manager)  # Sets limit to 100

    order = MagicMock()
    order.order_number = "A" * 200  # Make it long
    order.items = []
    order.contact_name = "Name"
    order.created_at = datetime.now()

    text = utils.generate_order_details_text(order)

    assert len(text) < 100
    assert "[text_truncated_suffix]" in text


async def test_send_order_details_view_success(mock_manager, mock_keyboards):
    """Test successfully editing the message."""
    message = AsyncMock()
    order = MagicMock()

    # Ensure get_message returns valid ints for limits
    mock_manager.get_message.side_effect = lambda s, k, **kw: (
        "4096" if "length" in k or "threshold" in k else ""
    )

    await utils.send_order_details_view(message, order)

    message.edit_text.assert_awaited_once()
    message.answer.assert_not_awaited()


async def test_send_order_details_view_fallback(mock_manager, mock_keyboards):
    """Test fallback to answer() if edit_text fails."""
    message = AsyncMock()
    message.edit_text.side_effect = Exception("Edit failed")
    order = MagicMock()
    mock_manager.get_message.side_effect = lambda s, k, **kw: (
        "4096" if "length" in k or "threshold" in k else ""
    )

    await utils.send_order_details_view(message, order)

    message.edit_text.assert_awaited_once()
    message.answer.assert_awaited_once()
