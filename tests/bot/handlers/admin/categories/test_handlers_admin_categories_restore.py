"""
Unit tests for the 'Restore Category' admin handler.

This module verifies the flow for restoring soft-deleted categories, ensuring that:
- The list of deleted categories is displayed correctly.
- Restoration logic handles success, failure (not found), and errors.
- Appropriate user feedback is provided in all scenarios.
"""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ecombot.bot.callback_data import AdminCallbackFactory
from ecombot.bot.callback_data import ConfirmationCallbackFactory
from ecombot.bot.handlers.admin.categories import restore
from ecombot.db.models import Category


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager used for retrieving messages."""
    return mocker.patch("ecombot.bot.handlers.admin.categories.restore.manager")


@pytest.fixture
def mock_crud(mocker: MockerFixture):
    """Mocks the CRUD operations."""
    return mocker.patch("ecombot.bot.handlers.admin.categories.restore.crud")


@pytest.fixture
def mock_keyboards(mocker: MockerFixture):
    """Mocks the keyboard generation functions."""
    mocker.patch(
        "ecombot.bot.handlers.admin.categories.restore.get_admin_panel_keyboard"
    )


async def test_restore_category_start_success(
    mock_manager, mock_crud, mock_keyboards, mock_session, mocker
):
    """Test displaying the list of deleted categories."""
    query = AsyncMock()
    callback_message = AsyncMock()
    callback_data = MagicMock(spec=AdminCallbackFactory)

    # Mock deleted categories
    cat1 = MagicMock(spec=Category)
    cat1.id = 1
    cat1.name = "Deleted Cat 1"
    cat2 = MagicMock(spec=Category)
    cat2.id = 2
    cat2.name = "Deleted Cat 2"

    mock_crud.get_deleted_categories = AsyncMock(return_value=[cat1, cat2])

    # Ensure get_message returns a string for InlineKeyboardButton validation
    mock_manager.get_message.return_value = "Restore Category"

    # Mock DTO validation to return the mock object itself (duck typing)
    mocker.patch(
        "ecombot.bot.handlers.admin.categories.restore.CategoryDTO.model_validate",
        side_effect=lambda x: x,
    )

    await restore.restore_category_start(
        query, callback_data, mock_session, callback_message
    )

    mock_crud.get_deleted_categories.assert_awaited_once_with(mock_session)
    callback_message.edit_text.assert_awaited_once()
    query.answer.assert_awaited_once()


async def test_restore_category_start_none_found(
    mock_manager, mock_crud, mock_keyboards, mock_session
):
    """Test behavior when no deleted categories exist."""
    query = AsyncMock()
    callback_message = AsyncMock()
    callback_data = MagicMock(spec=AdminCallbackFactory)

    mock_crud.get_deleted_categories = AsyncMock(return_value=[])

    await restore.restore_category_start(
        query, callback_data, mock_session, callback_message
    )

    callback_message.edit_text.assert_awaited_once()
    mock_manager.get_message.assert_any_call(
        "admin_categories", "restore_category_none_found"
    )
    query.answer.assert_awaited_once()


async def test_restore_category_start_error(
    mock_manager, mock_crud, mock_keyboards, mock_session
):
    """Test handling of database errors during fetch."""
    query = AsyncMock()
    callback_message = AsyncMock()
    callback_data = MagicMock(spec=AdminCallbackFactory)

    mock_crud.get_deleted_categories.side_effect = Exception("DB Error")

    await restore.restore_category_start(
        query, callback_data, mock_session, callback_message
    )

    callback_message.edit_text.assert_awaited_once()
    mock_manager.get_message.assert_any_call(
        "admin_categories", "restore_category_load_error"
    )
    query.answer.assert_awaited_once()


async def test_restore_category_confirm_success(
    mock_manager, mock_crud, mock_keyboards, mock_session
):
    """Test successful restoration of a category."""
    query = AsyncMock()
    callback_message = AsyncMock()
    callback_data = MagicMock(spec=ConfirmationCallbackFactory)
    callback_data.item_id = 1

    mock_crud.restore_category = AsyncMock(return_value=True)

    await restore.restore_category_confirm(
        query, callback_data, mock_session, callback_message
    )

    mock_crud.restore_category.assert_awaited_once_with(mock_session, 1)
    callback_message.edit_text.assert_awaited_once()
    mock_manager.get_message.assert_any_call(
        "admin_categories", "restore_category_success"
    )
    query.answer.assert_awaited_once()


async def test_restore_category_confirm_not_found(
    mock_manager, mock_crud, mock_keyboards, mock_session
):
    """Test restoration when category is not found (or already restored)."""
    query = AsyncMock()
    callback_message = AsyncMock()
    callback_data = MagicMock(spec=ConfirmationCallbackFactory)
    callback_data.item_id = 1

    mock_crud.restore_category = AsyncMock(return_value=False)

    await restore.restore_category_confirm(
        query, callback_data, mock_session, callback_message
    )

    callback_message.edit_text.assert_awaited_once()
    mock_manager.get_message.assert_any_call(
        "admin_categories", "restore_category_not_found"
    )
    query.answer.assert_awaited_once()
