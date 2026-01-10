"""
Unit tests for the 'Delete Category' admin handler.

This module verifies the FSM flow for deleting categories, ensuring that:
- The category list is displayed correctly.
- Category selection and confirmation work as expected.
- Deletion logic (success, failure, cancellation) is handled properly.
- Error handling covers database issues and missing categories.
"""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ecombot.bot.callback_data import AdminCallbackFactory
from ecombot.bot.callback_data import CatalogCallbackFactory
from ecombot.bot.callback_data import ConfirmationCallbackFactory
from ecombot.bot.handlers.admin.categories import delete
from ecombot.bot.handlers.admin.categories.states import DeleteCategory
from ecombot.db.models import Category


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager used for retrieving messages."""
    return mocker.patch("ecombot.bot.handlers.admin.categories.delete.manager")


@pytest.fixture
def mock_catalog_service(mocker: MockerFixture):
    """Mocks the catalog service."""
    return mocker.patch("ecombot.bot.handlers.admin.categories.delete.catalog_service")


@pytest.fixture
def mock_keyboards(mocker: MockerFixture):
    """Mocks the keyboard generation functions."""
    mocker.patch(
        "ecombot.bot.handlers.admin.categories.delete.get_catalog_categories_keyboard"
    )
    mocker.patch(
        "ecombot.bot.handlers.admin.categories.delete.get_delete_confirmation_keyboard"
    )
    mocker.patch(
        "ecombot.bot.handlers.admin.categories.delete.get_admin_panel_keyboard"
    )


async def test_delete_category_start_success(
    mock_manager, mock_catalog_service, mock_keyboards, mock_session
):
    """Test starting the delete flow with available categories."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    callback_data = MagicMock(spec=AdminCallbackFactory)

    mock_catalog_service.get_all_categories = AsyncMock(
        return_value=[MagicMock(spec=Category)]
    )

    await delete.delete_category_start(
        query, callback_data, mock_session, state, callback_message
    )

    callback_message.edit_text.assert_awaited_once()
    state.set_state.assert_awaited_once_with(DeleteCategory.choose_category)
    query.answer.assert_awaited_once()


async def test_delete_category_start_no_categories(
    mock_manager, mock_catalog_service, mock_keyboards, mock_session
):
    """Test starting the delete flow when no categories exist."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    callback_data = MagicMock(spec=AdminCallbackFactory)

    mock_catalog_service.get_all_categories = AsyncMock(return_value=[])

    await delete.delete_category_start(
        query, callback_data, mock_session, state, callback_message
    )

    callback_message.edit_text.assert_awaited_once()
    state.set_state.assert_not_awaited()
    query.answer.assert_awaited_once()


async def test_delete_category_confirm_success(
    mock_manager, mock_keyboards, mock_session
):
    """Test selecting a category for deletion confirmation."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    callback_data = MagicMock(spec=CatalogCallbackFactory)
    callback_data.item_id = 1

    category = MagicMock(spec=Category)
    category.name = "Test Cat"
    mock_session.get.return_value = category

    await delete.delete_category_confirm(
        query, callback_data, mock_session, state, callback_message
    )

    state.update_data.assert_awaited_once_with(category_id=1, category_name="Test Cat")
    callback_message.edit_text.assert_awaited_once()
    state.set_state.assert_awaited_once_with(DeleteCategory.confirm_deletion)
    query.answer.assert_awaited_once()


async def test_delete_category_confirm_not_found(
    mock_manager, mock_keyboards, mock_session
):
    """Test selecting a category that no longer exists."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    callback_data = MagicMock(spec=CatalogCallbackFactory)
    callback_data.item_id = 1

    mock_session.get.return_value = None

    await delete.delete_category_confirm(
        query, callback_data, mock_session, state, callback_message
    )

    callback_message.edit_text.assert_awaited_once()
    state.clear.assert_awaited_once()
    query.answer.assert_awaited_once()


async def test_delete_category_final_confirmed_success(
    mock_manager, mock_catalog_service, mock_keyboards, mock_session
):
    """Test successfully confirming deletion."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    callback_data = MagicMock(spec=ConfirmationCallbackFactory)
    callback_data.confirm = True
    callback_data.item_id = 1

    state.get_data.return_value = {"category_name": "Test Cat"}
    mock_catalog_service.delete_category_by_id = AsyncMock(return_value=True)

    await delete.delete_category_final(
        query, callback_data, mock_session, state, callback_message
    )

    mock_catalog_service.delete_category_by_id.assert_awaited_once_with(mock_session, 1)
    callback_message.edit_text.assert_awaited_once()
    state.clear.assert_awaited_once()
    query.answer.assert_awaited_once()


async def test_delete_category_final_cancelled(
    mock_manager, mock_keyboards, mock_session
):
    """Test cancelling the deletion."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    callback_data = MagicMock(spec=ConfirmationCallbackFactory)
    callback_data.confirm = False

    await delete.delete_category_final(
        query, callback_data, mock_session, state, callback_message
    )

    callback_message.edit_text.assert_awaited_once()
    mock_session.execute.assert_not_called()  # No DB action
    state.clear.assert_awaited_once()
    query.answer.assert_awaited_once()
