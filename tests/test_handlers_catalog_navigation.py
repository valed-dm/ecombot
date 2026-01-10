"""
Unit tests for catalog navigation handlers.

This module verifies:
- The /start command handler.
- The 'Back to Categories' callback handler.
"""

from unittest.mock import AsyncMock

import pytest
from pytest_mock import MockerFixture

from ecombot.bot.handlers.catalog import navigation


@pytest.fixture
def mock_show_main_catalog(mocker: MockerFixture):
    """Mocks the show_main_catalog utility."""
    return mocker.patch(
        "ecombot.bot.handlers.catalog.navigation.show_main_catalog",
        new_callable=AsyncMock,
    )


async def test_command_start_handler(mock_show_main_catalog, mock_session):
    """Test the /start command."""
    message = AsyncMock()
    await navigation.command_start_handler(message, mock_session)
    mock_show_main_catalog.assert_awaited_once_with(message, mock_session)


async def test_back_to_main_handler(mock_show_main_catalog, mock_session):
    """Test the back to main catalog callback."""
    query = AsyncMock()
    callback_message = AsyncMock()

    await navigation.back_to_main_handler(query, mock_session, callback_message)

    mock_show_main_catalog.assert_awaited_once_with(
        callback_message, mock_session, is_edit=True
    )
    query.answer.assert_awaited_once()
