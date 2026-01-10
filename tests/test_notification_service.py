from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
import pytest

from ecombot.schemas.dto import OrderDTO
from ecombot.schemas.enums import OrderStatus
from ecombot.services import notification_service


@pytest.fixture
def mock_bot():
    return AsyncMock(spec=Bot)


@pytest.fixture
def mock_order():
    user = MagicMock()
    user.telegram_id = 12345
    order = MagicMock(spec=OrderDTO)
    order.user = user
    order.order_number = "ORD-123"
    return order


async def test_send_order_status_update_processing(mock_bot, mock_order):
    """Test notification for PROCESSING status."""
    mock_order.status = OrderStatus.PROCESSING

    await notification_service.send_order_status_update(mock_bot, mock_order)

    mock_bot.send_message.assert_awaited_once()
    args, kwargs = mock_bot.send_message.call_args
    assert kwargs["chat_id"] == 12345
    assert "Processing" in kwargs["text"]


async def test_send_order_status_update_shipped(mock_bot, mock_order):
    """Test notification for SHIPPED status."""
    mock_order.status = OrderStatus.SHIPPED

    await notification_service.send_order_status_update(mock_bot, mock_order)

    mock_bot.send_message.assert_awaited_once()
    args, kwargs = mock_bot.send_message.call_args
    assert "shipped" in kwargs["text"]


async def test_send_order_status_update_completed(mock_bot, mock_order):
    """Test notification for COMPLETED status."""
    mock_order.status = OrderStatus.COMPLETED

    await notification_service.send_order_status_update(mock_bot, mock_order)

    mock_bot.send_message.assert_awaited_once()
    args, kwargs = mock_bot.send_message.call_args
    assert "Complete" in kwargs["text"]


async def test_send_order_status_update_cancelled(mock_bot, mock_order):
    """Test notification for CANCELLED status."""
    mock_order.status = OrderStatus.CANCELLED

    await notification_service.send_order_status_update(mock_bot, mock_order)

    mock_bot.send_message.assert_awaited_once()
    args, kwargs = mock_bot.send_message.call_args
    assert "cancelled" in kwargs["text"]


async def test_send_order_status_update_no_notification(mock_bot, mock_order):
    """Test statuses that do not trigger a notification (e.g. PENDING)."""
    mock_order.status = OrderStatus.PENDING

    await notification_service.send_order_status_update(mock_bot, mock_order)

    mock_bot.send_message.assert_not_awaited()


async def test_send_order_status_update_bad_request(mock_bot, mock_order):
    """Test handling of TelegramBadRequest (e.g. user blocked bot)."""
    mock_order.status = OrderStatus.PROCESSING
    mock_bot.send_message.side_effect = TelegramBadRequest(
        method="sendMessage", message="Blocked"
    )

    # Should not raise exception
    await notification_service.send_order_status_update(mock_bot, mock_order)
    mock_bot.send_message.assert_awaited_once()


async def test_send_order_status_update_generic_error(mock_bot, mock_order):
    """Test handling of generic exceptions."""
    mock_order.status = OrderStatus.PROCESSING
    mock_bot.send_message.side_effect = Exception("Network error")

    # Should not raise exception
    await notification_service.send_order_status_update(mock_bot, mock_order)
    mock_bot.send_message.assert_awaited_once()
