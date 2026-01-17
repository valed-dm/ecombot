"""
Unit tests for admin orders navigation handlers.

This module verifies:
- The 'Back to Admin Panel' navigation logic.
"""

from unittest.mock import AsyncMock

import pytest
from pytest_mock import MockerFixture

from ecombot.bot.handlers.admin.orders import navigation


@pytest.fixture
def mock_send_panel(mocker: MockerFixture):
    """Mocks the send_main_admin_panel helper."""
    return mocker.patch(
        "ecombot.bot.handlers.admin_orders.navigation.send_main_admin_panel"
    )


async def test_back_to_main_admin_panel_handler(mock_send_panel):
    """Test that the handler calls the helper and answers the query."""
    query = AsyncMock()
    callback_message = AsyncMock()

    await navigation.back_to_main_admin_panel_handler(query, callback_message)

    mock_send_panel.assert_awaited_once_with(callback_message)
    query.answer.assert_awaited_once()
