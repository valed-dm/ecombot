"""
Unit tests for order details handlers.

This module verifies:
- Viewing details of a specific order (success case).
- Handling cases where the order is not found or access is denied.
"""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ecombot.bot.callback_data import OrderCallbackFactory
from ecombot.bot.handlers.orders import details
from ecombot.db.models import User
from ecombot.schemas.dto import OrderDTO


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager."""
    manager = mocker.patch("ecombot.bot.handlers.orders.details.manager")
    manager.get_message.return_value = "Message text"
    return manager


@pytest.fixture
def mock_order_service(mocker: MockerFixture):
    """Mocks the order service."""
    return mocker.patch("ecombot.bot.handlers.orders.details.order_service")


@pytest.fixture
def mock_utils(mocker: MockerFixture):
    """Mocks the order utils."""
    return mocker.patch("ecombot.bot.handlers.orders.details.format_order_details_text")


@pytest.fixture
def mock_keyboards(mocker: MockerFixture):
    """Mocks the keyboard generator."""
    return mocker.patch(
        "ecombot.bot.handlers.orders.details.get_order_details_keyboard"
    )


async def test_view_order_details_handler_success(
    mock_manager,
    mock_order_service,
    mock_utils,
    mock_keyboards,
    mock_session,
):
    """Test viewing order details successfully."""
    query = AsyncMock()
    callback_message = AsyncMock()
    db_user = MagicMock(spec=User)
    db_user.id = 123
    callback_data = OrderCallbackFactory(action="view_details", item_id=10)

    mock_dto = MagicMock(spec=OrderDTO)
    mock_order_service.get_order_details = AsyncMock(return_value=mock_dto)
    mock_utils.return_value = "Order Details Text"

    await details.view_order_details_handler(
        query, callback_data, mock_session, db_user, callback_message
    )

    mock_order_service.get_order_details.assert_awaited_once_with(mock_session, 10, 123)
    mock_utils.assert_called_once_with(mock_dto)
    callback_message.edit_text.assert_awaited_once()
    query.answer.assert_awaited_once()


async def test_view_order_details_handler_not_found(
    mock_manager,
    mock_order_service,
    mock_session,
):
    """Test viewing order details when order is not found."""
    query = AsyncMock()
    callback_message = AsyncMock()
    db_user = MagicMock(spec=User)
    db_user.id = 123
    callback_data = OrderCallbackFactory(action="view_details", item_id=999)

    mock_order_service.get_order_details = AsyncMock(return_value=None)

    await details.view_order_details_handler(
        query, callback_data, mock_session, db_user, callback_message
    )

    mock_order_service.get_order_details.assert_awaited_once_with(
        mock_session, 999, 123
    )
    callback_message.edit_text.assert_not_awaited()
    query.answer.assert_awaited_once()
    # Verify alert is shown
    assert query.answer.call_args[1].get("show_alert") is True
