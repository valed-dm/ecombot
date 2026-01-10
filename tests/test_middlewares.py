"""
Unit tests for bot middlewares.

This module verifies:
- DbSessionMiddleware: Session creation, injection, commit, and rollback.
- MessageInteractionMiddleware: Validation of CallbackQuery messages.
- UserMiddleware: User retrieval/creation and command setting.
"""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.types import User as TelegramUser
import pytest
from pytest_mock import MockerFixture

from ecombot.bot.middlewares import DbSessionMiddleware
from ecombot.bot.middlewares import MessageInteractionMiddleware
from ecombot.bot.middlewares import UserMiddleware
from ecombot.db.models import User as DBUser


# --- DbSessionMiddleware Tests ---


async def test_db_session_middleware_commit():
    """Test that session is injected and committed on success."""
    mock_session = AsyncMock()
    # Mock the async context manager of the session pool
    session_pool = MagicMock()
    session_pool.return_value.__aenter__.return_value = mock_session

    middleware = DbSessionMiddleware(session_pool)
    handler = AsyncMock(return_value="Success")
    event = MagicMock()
    data = {}

    result = await middleware(handler, event, data)

    assert result == "Success"
    assert data["session"] == mock_session
    handler.assert_awaited_once_with(event, data)
    mock_session.commit.assert_awaited_once()
    mock_session.rollback.assert_not_awaited()


async def test_db_session_middleware_rollback():
    """Test that session is rolled back on exception."""
    mock_session = AsyncMock()
    session_pool = MagicMock()
    session_pool.return_value.__aenter__.return_value = mock_session

    middleware = DbSessionMiddleware(session_pool)
    handler = AsyncMock(side_effect=Exception("Handler Error"))
    event = MagicMock()
    data = {}

    with pytest.raises(Exception, match="Handler Error"):
        await middleware(handler, event, data)

    mock_session.commit.assert_not_awaited()
    mock_session.rollback.assert_awaited_once()


# --- MessageInteractionMiddleware Tests ---


async def test_message_interaction_middleware_success():
    """Test passing when CallbackQuery has a valid message."""
    middleware = MessageInteractionMiddleware()
    handler = AsyncMock(return_value="OK")

    # Setup CallbackQuery with a Message
    event = AsyncMock(spec=CallbackQuery)
    event.message = AsyncMock(spec=Message)
    data = {}

    result = await middleware(handler, event, data)

    assert result == "OK"
    assert data["callback_message"] == event.message
    handler.assert_awaited_once()


async def test_message_interaction_middleware_no_message():
    """Test blocking when CallbackQuery has no message (stale)."""
    middleware = MessageInteractionMiddleware()
    handler = AsyncMock()

    event = AsyncMock(spec=CallbackQuery)
    event.message = None  # Stale callback
    event.answer = AsyncMock()
    data = {}

    result = await middleware(handler, event, data)

    assert result is None
    handler.assert_not_awaited()
    event.answer.assert_awaited_once()
    assert event.answer.call_args[1].get("show_alert") is True


async def test_message_interaction_middleware_not_callback():
    """Test that non-CallbackQuery events are passed through."""
    middleware = MessageInteractionMiddleware()
    handler = AsyncMock(return_value="OK")

    event = AsyncMock(spec=Message)  # Not a CallbackQuery
    data = {}

    result = await middleware(handler, event, data)

    assert result == "OK"
    handler.assert_awaited_once()


# --- UserMiddleware Tests ---


@pytest.fixture
def mock_settings(mocker: MockerFixture):
    return mocker.patch("ecombot.bot.middlewares.settings")


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    return mocker.patch("ecombot.bot.middlewares.manager")


@pytest.fixture
def mock_crud_user(mocker: MockerFixture):
    return mocker.patch(
        "ecombot.bot.middlewares.crud.get_or_create_user", new_callable=AsyncMock
    )


async def test_user_middleware_success(mock_settings, mock_manager, mock_crud_user):
    """Test user injection and command setting."""
    middleware = UserMiddleware()
    handler = AsyncMock(return_value="OK")

    tg_user = MagicMock(spec=TelegramUser)
    tg_user.id = 12345

    session = AsyncMock()
    bot = AsyncMock()

    data = {"event_from_user": tg_user, "session": session, "bot": bot}
    event = MagicMock()

    # Mock DB user return
    db_user = MagicMock(spec=DBUser)
    mock_crud_user.return_value = db_user

    # Mock settings
    mock_settings.ADMIN_IDS = [12345]  # User is admin
    mock_manager.get_commands.return_value = []

    await middleware(handler, event, data)

    # Verify user injection
    assert data["db_user"] == db_user
    mock_crud_user.assert_awaited_once_with(session, tg_user)

    # Verify commands were set (since cache was empty)
    bot.set_my_commands.assert_awaited_once()
    mock_manager.get_commands.assert_called_with("admin")


async def test_user_middleware_skip_no_user(mock_crud_user):
    """Test skipping middleware if no user in event."""
    middleware = UserMiddleware()
    handler = AsyncMock()
    event = MagicMock()
    data = {}  # Missing event_from_user

    await middleware(handler, event, data)

    handler.assert_awaited_once()
    mock_crud_user.assert_not_awaited()
    assert "db_user" not in data
