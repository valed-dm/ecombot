"""
Unit tests for admin order status management handlers.

This module verifies:
- Successful order status updates and notifications.
- Handling of invalid query data and order IDs.
- Error handling during service calls and view refreshing.
"""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ecombot.bot.handlers.admin_orders import status_management
from ecombot.bot.handlers.admin_orders.utils import InvalidQueryDataError
from ecombot.schemas.enums import OrderStatus


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager."""
    manager = mocker.patch(
        "ecombot.bot.handlers.admin_orders.status_management.manager"
    )
    manager.get_message.return_value = "Message text"
    return manager


@pytest.fixture
def mock_order_service(mocker: MockerFixture):
    """Mocks the order service."""
    return mocker.patch(
        "ecombot.bot.handlers.admin_orders.status_management.order_service"
    )


@pytest.fixture
def mock_notification_service(mocker: MockerFixture):
    """Mocks the notification service."""
    mock = mocker.patch(
        "ecombot.bot.handlers.admin_orders.status_management.notification_service"
    )
    mock.send_order_status_update = AsyncMock()
    return mock


@pytest.fixture
def mock_send_details(mocker: MockerFixture):
    """Mocks the send_order_details_view helper."""
    return mocker.patch(
        "ecombot.bot.handlers.admin_orders.status_management.send_order_details_view",
        new_callable=AsyncMock,
    )


@pytest.fixture
def mock_crud(mocker: MockerFixture):
    """Mocks the CRUD operations."""
    return mocker.patch("ecombot.bot.handlers.admin_orders.status_management.crud")


async def test_change_order_status_success(
    mock_manager,
    mock_order_service,
    mock_notification_service,
    mock_send_details,
    mock_session,
):
    """Test successful order status change."""
    query = AsyncMock()
    query.data = "admin_order_status:123:paid"
    callback_message = AsyncMock()
    bot = AsyncMock()

    updated_dto = MagicMock()
    mock_order_service.change_order_status = AsyncMock(return_value=updated_dto)

    await status_management.change_order_status_handler(
        query, mock_session, callback_message, bot
    )

    mock_order_service.change_order_status.assert_awaited_once_with(
        mock_session, 123, OrderStatus.PAID
    )
    query.answer.assert_awaited_once()
    mock_notification_service.send_order_status_update.assert_awaited_once_with(
        bot, updated_dto
    )
    mock_send_details.assert_awaited_once_with(callback_message, updated_dto)


async def test_change_order_status_invalid_query_data(mock_manager):
    """Test handling of None query data."""
    query = AsyncMock()
    query.data = None
    callback_message = AsyncMock()
    bot = AsyncMock()
    session = AsyncMock()

    with pytest.raises(InvalidQueryDataError):
        await status_management.change_order_status_handler(
            query, session, callback_message, bot
        )


async def test_change_order_status_invalid_id(mock_manager, mock_session):
    """Test handling of non-integer order ID."""
    query = AsyncMock()
    query.data = "admin_order_status:abc:paid"
    callback_message = AsyncMock()
    bot = AsyncMock()

    await status_management.change_order_status_handler(
        query, mock_session, callback_message, bot
    )

    query.answer.assert_awaited_once()
    # Should show alert
    assert query.answer.call_args[1].get("show_alert") is True


async def test_change_order_status_service_error(
    mock_manager,
    mock_order_service,
    mock_crud,
    mock_send_details,
    mock_session,
    mocker,
):
    """Test handling of service layer exception and view refresh."""
    query = AsyncMock()
    query.data = "admin_order_status:123:paid"
    callback_message = AsyncMock()
    bot = AsyncMock()

    # Service raises exception
    mock_order_service.change_order_status.side_effect = Exception("Service Error")

    # Mock refresh logic
    mock_order = MagicMock()
    mock_crud.get_order = AsyncMock(return_value=mock_order)

    # Mock DTO validation
    fake_dto = MagicMock()
    mocker.patch(
        "ecombot.bot.handlers.admin_orders.status_management.OrderDTO.model_validate",
        return_value=fake_dto,
    )

    await status_management.change_order_status_handler(
        query, mock_session, callback_message, bot
    )

    # Should show error alert
    query.answer.assert_awaited()
    assert query.answer.call_args[1].get("show_alert") is True

    # Should attempt to refresh view
    mock_crud.get_order.assert_awaited_once_with(mock_session, 123)
    mock_send_details.assert_awaited_once_with(callback_message, fake_dto)
