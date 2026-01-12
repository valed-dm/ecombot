"""
Unit tests for order handler utilities.

This module verifies:
- Text formatting for order lists and details.
- Handling of soft-deleted products in order details.
- Sending the order history view (edit vs new message).
"""

from datetime import datetime
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from aiogram.exceptions import TelegramBadRequest
import pytest
from pytest_mock import MockerFixture

import ecombot.bot.handlers.orders.utils as utils
from ecombot.schemas.dto import OrderDTO
from ecombot.schemas.enums import OrderStatus


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager."""
    manager = mocker.patch("ecombot.bot.handlers.orders.utils.manager")

    def side_effect(section, key, **kwargs):
        if key == "date_format":
            return "%Y-%m-%d"
        if key == "deleted_product_suffix":
            return " (Deleted)"
        if key == "order_item_template":
            # Include name to verify suffix presence
            return f"[{key} {kwargs.get('name')}]"
        return f"[{key}]"

    manager.get_message.side_effect = side_effect
    return manager


@pytest.fixture
def mock_order_service(mocker: MockerFixture):
    """Mocks the order service."""
    return mocker.patch("ecombot.bot.handlers.orders.utils.order_service")


def test_format_order_list_text_empty(mock_manager):
    """Test formatting list text when no orders exist."""
    text = utils.format_order_list_text([])
    assert "[order_history_header]" in text
    assert "[no_orders_message]" in text


def test_format_order_list_text_populated(mock_manager):
    """Test formatting list text with orders."""
    orders = [MagicMock(spec=OrderDTO)]
    text = utils.format_order_list_text(orders)
    assert "[order_history_header]" in text
    assert "[no_orders_message]" not in text


def test_format_order_details_text_standard(mock_manager):
    """Test formatting details for a standard order."""
    order = MagicMock(spec=OrderDTO)
    order.id = 123
    order.status = OrderStatus.PAID
    order.created_at = datetime(2023, 1, 1)
    order.shipping_address = "123 Main St"

    item = MagicMock()
    item.product.name = "Product A"
    item.product.deleted_at = None
    item.quantity = 2
    item.price = 10.0
    order.items = [item]

    text = utils.format_order_details_text(order)

    assert "[order_details_header]" in text
    assert "[order_date_line]" in text
    assert "[order_address_line]" in text
    assert "[status_line]" in text
    assert "[order_items_header]" in text
    assert "[order_item_template Product A]" in text
    assert "[total_label]" in text
    assert "[deleted_items_notice]" not in text


def test_format_order_details_text_deleted_items(mock_manager):
    """Test formatting details with deleted items."""
    order = MagicMock(spec=OrderDTO)
    order.id = 123
    order.status = OrderStatus.PAID
    order.created_at = datetime(2023, 1, 1)
    order.shipping_address = "123 Main St"

    # Active item
    item1 = MagicMock()
    item1.product.name = "P1"
    item1.product.deleted_at = None
    item1.quantity = 1
    item1.price = 10.0

    # Deleted item
    item2 = MagicMock()
    item2.product.name = "P2"
    item2.product.deleted_at = datetime.now()
    item2.quantity = 1
    item2.price = 20.0

    order.items = [item1, item2]

    text = utils.format_order_details_text(order)

    # Verify suffix is present in the template call
    assert "P2 (Deleted)" in text
    assert "[active_items_total]" in text
    assert "[deleted_items_total]" in text
    assert "[total_paid]" in text


async def test_send_orders_view_empty(mock_manager, mock_order_service, mock_session):
    """Test sending view when user has no orders."""
    message = AsyncMock()
    db_user = MagicMock()
    db_user.id = 1

    mock_order_service.list_user_orders = AsyncMock(return_value=[])

    await utils.send_orders_view(message, mock_session, db_user)

    message.answer.assert_awaited_once()
    # Should contain no orders message (checked via format_order_list_text logic)
    args, _ = message.answer.call_args
    assert "[no_orders_message]" in args[0]


async def test_send_orders_view_populated(
    mock_manager, mock_order_service, mock_session
):
    """Test sending view with orders (successful edit)."""
    message = AsyncMock()
    db_user = MagicMock()
    db_user.id = 1

    order = MagicMock(spec=OrderDTO)
    order.id = 10
    order.status = OrderStatus.PAID
    order.total_price = 100.0

    mock_order_service.list_user_orders = AsyncMock(return_value=[order])

    await utils.send_orders_view(message, mock_session, db_user)

    message.edit_text.assert_awaited_once()
    message.answer.assert_not_awaited()


async def test_send_orders_view_fallback(
    mock_manager, mock_order_service, mock_session
):
    """Test fallback to answer when edit_text fails."""
    message = AsyncMock()
    db_user = MagicMock()

    order = MagicMock(spec=OrderDTO)
    order.id = 10
    order.status = OrderStatus.PAID
    order.total_price = 100.0

    mock_order_service.list_user_orders = AsyncMock(return_value=[order])

    # Simulate BadRequest on edit
    message.edit_text.side_effect = TelegramBadRequest(method="edit", message="Error")

    await utils.send_orders_view(message, mock_session, db_user)

    message.edit_text.assert_awaited_once()
    message.delete.assert_awaited_once()
    message.answer.assert_awaited_once()
