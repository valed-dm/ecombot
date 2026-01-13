from decimal import Decimal
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
    order.display_order_number = "ORD-123"
    order.contact_name = "John Doe"
    order.total_price = Decimal("100.00")
    order.items = [MagicMock(), MagicMock()]
    return order


@pytest.fixture
def mock_manager(mocker):
    """Mocks the central manager used in notification service."""
    # We patch the manager instance imported in the service module
    manager = mocker.patch("ecombot.services.notification_service.manager")
    # Configure get_message to return a predictable string
    manager.get_message.side_effect = lambda section, key, **kwargs: f"[{key}]"
    return manager


@pytest.fixture
def mock_settings(mocker):
    """Mocks the settings."""
    settings = mocker.patch("ecombot.services.notification_service.settings")
    return settings


async def test_send_order_status_update_processing(mock_bot, mock_order, mock_manager):
    """Test notification for PROCESSING status."""
    mock_order.status = OrderStatus.PROCESSING
    # Mock the status name lookup
    mock_manager.get_message.side_effect = lambda s, k, **kw: f"[{k}]"

    await notification_service.send_order_status_update(mock_bot, mock_order)

    mock_bot.send_message.assert_awaited_once()
    args, kwargs = mock_bot.send_message.call_args
    assert kwargs["chat_id"] == 12345
    assert "[notification_processing]" in kwargs["text"]


async def test_send_order_status_update_shipped(mock_bot, mock_order, mock_manager):
    """Test notification for SHIPPED status."""
    mock_order.status = OrderStatus.SHIPPED
    mock_manager.get_message.side_effect = lambda s, k, **kw: f"[{k}]"

    await notification_service.send_order_status_update(mock_bot, mock_order)

    mock_bot.send_message.assert_awaited_once()
    args, kwargs = mock_bot.send_message.call_args
    assert "[notification_shipped]" in kwargs["text"]


async def test_send_order_status_update_completed(mock_bot, mock_order, mock_manager):
    """Test notification for COMPLETED status."""
    mock_order.status = OrderStatus.COMPLETED
    mock_manager.get_message.side_effect = lambda s, k, **kw: f"[{k}]"

    await notification_service.send_order_status_update(mock_bot, mock_order)

    mock_bot.send_message.assert_awaited_once()
    args, kwargs = mock_bot.send_message.call_args
    assert "[notification_completed]" in kwargs["text"]


async def test_send_order_status_update_cancelled(mock_bot, mock_order, mock_manager):
    """Test notification for CANCELLED status."""
    mock_order.status = OrderStatus.CANCELLED
    mock_manager.get_message.side_effect = lambda s, k, **kw: f"[{k}]"

    await notification_service.send_order_status_update(mock_bot, mock_order)

    mock_bot.send_message.assert_awaited_once()
    args, kwargs = mock_bot.send_message.call_args
    assert "[notification_cancelled]" in kwargs["text"]


async def test_send_order_status_update_no_notification(mock_bot, mock_order):
    """Test statuses that do not trigger a notification (e.g. PENDING)."""
    mock_order.status = OrderStatus.PENDING

    await notification_service.send_order_status_update(mock_bot, mock_order)

    mock_bot.send_message.assert_not_awaited()


async def test_send_order_status_update_bad_request(mock_bot, mock_order, mock_manager):
    """Test handling of TelegramBadRequest (e.g. user blocked bot)."""
    mock_order.status = OrderStatus.PROCESSING
    mock_manager.get_message.side_effect = lambda s, k, **kw: f"[{k}]"

    mock_bot.send_message.side_effect = TelegramBadRequest(
        method="sendMessage", message="Blocked"
    )

    # Should not raise exception
    await notification_service.send_order_status_update(mock_bot, mock_order)
    mock_bot.send_message.assert_awaited_once()


async def test_notify_admins_new_order(
    mock_bot, mock_order, mock_manager, mock_settings
):
    """Test notifying admins about a new order."""
    mock_settings.ADMIN_IDS = [111, 222]
    mock_manager.get_message.side_effect = lambda s, k, **kw: f"[{k}]"

    await notification_service.notify_admins_new_order(mock_bot, mock_order)

    assert mock_bot.send_message.await_count == 2
    # Check calls
    mock_bot.send_message.assert_any_await(chat_id=111, text="[admin_new_order]")
    mock_bot.send_message.assert_any_await(chat_id=222, text="[admin_new_order]")


async def test_send_order_status_update_generic_error(
    mock_bot, mock_order, mock_manager
):
    """Test handling of generic exceptions."""
    mock_order.status = OrderStatus.PROCESSING
    mock_manager.get_message.side_effect = lambda s, k, **kw: f"[{k}]"

    mock_bot.send_message.side_effect = Exception("Network error")

    # Should not raise exception
    await notification_service.send_order_status_update(mock_bot, mock_order)
    mock_bot.send_message.assert_awaited_once()
