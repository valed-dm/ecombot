"""
Unit tests for order pagination handlers.

This module verifies:
- The pagination callback handler.
"""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ecombot.bot.callback_data import OrderCallbackFactory
from ecombot.bot.handlers.orders import listing
from ecombot.db.models import User


@pytest.fixture
def mock_send_orders_view(mocker: MockerFixture):
    """Mocks the send_orders_view utility."""
    return mocker.patch(
        "ecombot.bot.handlers.orders.listing.send_orders_view",
        new_callable=AsyncMock,
    )


async def test_orders_pagination_handler(mock_send_orders_view, mock_session):
    """Test the pagination callback."""
    query = AsyncMock()
    callback_message = AsyncMock()
    db_user = MagicMock(spec=User)
    callback_data = OrderCallbackFactory(action="list", item_id=2)

    await listing.orders_pagination_handler(
        query, callback_data, mock_session, db_user, callback_message
    )

    mock_send_orders_view.assert_awaited_once_with(
        callback_message, mock_session, db_user, page=2
    )
    query.answer.assert_awaited_once()
