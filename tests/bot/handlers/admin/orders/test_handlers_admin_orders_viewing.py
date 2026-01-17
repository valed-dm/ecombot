"""
Unit tests for admin order viewing handlers.

This module verifies:
- The entry point for viewing orders (status selection).
- Filtering orders by status (fetching, displaying list, handling empty results).
- Viewing details of a specific order (fetching, DTO conversion, error handling).
"""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ecombot.bot.callback_data import OrderCallbackFactory
from ecombot.bot.handlers.admin.orders import viewing
from ecombot.bot.handlers.admin.orders.utils import InvalidQueryDataError
from ecombot.schemas.enums import OrderStatus


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager."""
    manager = mocker.patch("ecombot.bot.handlers.admin_orders.viewing.manager")
    manager.get_message.return_value = "Message text"
    return manager


@pytest.fixture
def mock_order_service(mocker: MockerFixture):
    """Mocks the order service."""
    return mocker.patch("ecombot.bot.handlers.admin_orders.viewing.order_service")


@pytest.fixture
def mock_crud(mocker: MockerFixture):
    """Mocks the CRUD operations."""
    return mocker.patch("ecombot.bot.handlers.admin_orders.viewing.crud")


@pytest.fixture
def mock_send_details(mocker: MockerFixture):
    """Mocks the send_order_details_view helper."""
    return mocker.patch(
        "ecombot.bot.handlers.admin_orders.viewing.send_order_details_view",
        new_callable=AsyncMock,
    )


@pytest.fixture
def mock_keyboards(mocker: MockerFixture):
    """Mocks the keyboard generators."""
    mocker.patch(
        "ecombot.bot.handlers.admin_orders.viewing.get_admin_order_filters_keyboard"
    )
    mocker.patch(
        "ecombot.bot.handlers.admin_orders.viewing.get_admin_orders_list_keyboard"
    )


async def test_view_orders_start_handler(mock_manager, mock_keyboards):
    """Test the entry point for viewing orders."""
    query = AsyncMock()
    callback_message = AsyncMock()

    await viewing.view_orders_start_handler(query, callback_message)

    callback_message.edit_text.assert_awaited_once()
    query.answer.assert_awaited_once()


async def test_filter_orders_by_status_handler_success(
    mock_manager, mock_order_service, mock_keyboards, mock_session
):
    """Test filtering orders by status with results."""
    query = AsyncMock()
    query.data = "admin_order_filter:paid"
    callback_message = AsyncMock()

    # Mock service returning a list of orders
    mock_orders = [MagicMock(), MagicMock()]
    mock_order_service.get_orders_by_status_for_admin = AsyncMock(
        return_value=mock_orders
    )

    await viewing.filter_orders_by_status_handler(query, mock_session, callback_message)

    mock_order_service.get_orders_by_status_for_admin.assert_awaited_once_with(
        mock_session, OrderStatus.PAID
    )
    # Should edit text twice: once for progress, once for result
    assert callback_message.edit_text.await_count == 2
    query.answer.assert_awaited_once()


async def test_filter_orders_by_status_handler_empty(
    mock_manager, mock_order_service, mock_keyboards, mock_session
):
    """Test filtering orders by status with no results."""
    query = AsyncMock()
    query.data = "admin_order_filter:pending"
    callback_message = AsyncMock()

    mock_order_service.get_orders_by_status_for_admin = AsyncMock(return_value=[])

    await viewing.filter_orders_by_status_handler(query, mock_session, callback_message)

    # Verify "no orders found" message logic
    mock_manager.get_message.assert_any_call("admin_orders", "no_orders_found")
    assert callback_message.edit_text.await_count == 2
    query.answer.assert_awaited_once()


async def test_filter_orders_by_status_handler_invalid_data(mock_manager, mock_session):
    """Test handling of missing query data."""
    query = AsyncMock()
    query.data = None
    callback_message = AsyncMock()

    with pytest.raises(InvalidQueryDataError):
        await viewing.filter_orders_by_status_handler(
            query, mock_session, callback_message
        )


async def test_admin_view_order_details_handler_success(
    mock_manager, mock_crud, mock_send_details, mock_session, mocker
):
    """Test viewing details of a specific order."""
    query = AsyncMock()
    callback_message = AsyncMock()
    callback_data = MagicMock(spec=OrderCallbackFactory)
    callback_data.item_id = 123

    mock_order = MagicMock()
    mock_crud.get_order = AsyncMock(return_value=mock_order)

    fake_dto = MagicMock()
    mocker.patch(
        "ecombot.bot.handlers.admin_orders.viewing.OrderDTO.model_validate",
        return_value=fake_dto,
    )

    await viewing.admin_view_order_details_handler(
        query, callback_data, mock_session, callback_message
    )

    mock_crud.get_order.assert_awaited_once_with(mock_session, 123)
    mock_send_details.assert_awaited_once_with(callback_message, fake_dto)
    query.answer.assert_awaited_once()


async def test_admin_view_order_details_handler_not_found(
    mock_manager, mock_crud, mock_send_details, mock_session
):
    """Test viewing details when order is not found."""
    query = AsyncMock()
    callback_message = AsyncMock()
    callback_data = MagicMock(spec=OrderCallbackFactory)
    callback_data.item_id = 999

    mock_crud.get_order = AsyncMock(return_value=None)

    await viewing.admin_view_order_details_handler(
        query, callback_data, mock_session, callback_message
    )

    mock_send_details.assert_not_awaited()
    query.answer.assert_awaited_once()
    assert query.answer.call_args[1].get("show_alert") is True
