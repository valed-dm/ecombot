"""
Unit tests for order listing handlers.

This module verifies:
- The /orders command handler.
- The 'Back to Order History' callback handler.
"""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ecombot.bot.handlers.orders import listing
from ecombot.db.models import User


@pytest.fixture
def mock_send_orders_view(mocker: MockerFixture):
    """Mocks the send_orders_view utility."""
    return mocker.patch(
        "ecombot.bot.handlers.orders.listing.send_orders_view",
        new_callable=AsyncMock,
    )


async def test_view_orders_handler(mock_send_orders_view, mock_session):
    """Test the /orders command."""
    message = AsyncMock()
    db_user = MagicMock(spec=User)

    await listing.view_orders_handler(message, mock_session, db_user)

    mock_send_orders_view.assert_awaited_once_with(message, mock_session, db_user)


async def test_back_to_orders_handler(mock_send_orders_view, mock_session):
    """Test the back to orders list callback."""
    query = AsyncMock()
    callback_message = AsyncMock()
    db_user = MagicMock(spec=User)

    await listing.back_to_orders_handler(query, mock_session, db_user, callback_message)

    mock_send_orders_view.assert_awaited_once_with(
        callback_message, mock_session, db_user
    )
    query.answer.assert_awaited_once()
