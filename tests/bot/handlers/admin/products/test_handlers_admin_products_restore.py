"""
Unit tests for the 'Restore Product' admin handler.

This module verifies the flow for restoring soft-deleted products, ensuring that:
- The list of deleted products is displayed correctly.
- Restoration logic handles success, failure (not found), and errors.
- Appropriate user feedback is provided in all scenarios.
"""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ecombot.bot.callback_data import AdminCallbackFactory
from ecombot.bot.callback_data import ConfirmationCallbackFactory
from ecombot.bot.handlers.admin.products import restore
from ecombot.db.models import Product


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager used for retrieving messages."""
    return mocker.patch("ecombot.bot.handlers.admin.products.restore.manager")


@pytest.fixture
def mock_crud(mocker: MockerFixture):
    """Mocks the CRUD operations."""
    return mocker.patch("ecombot.bot.handlers.admin.products.restore.crud")


@pytest.fixture
def mock_keyboards(mocker: MockerFixture):
    """Mocks the keyboard generation functions."""
    mocker.patch("ecombot.bot.handlers.admin.products.restore.get_admin_panel_keyboard")


async def test_restore_product_start_success(
    mock_manager, mock_crud, mock_keyboards, mock_session, mocker
):
    """Test displaying the list of deleted products."""
    query = AsyncMock()
    callback_message = AsyncMock()
    callback_data = MagicMock(spec=AdminCallbackFactory)

    # Mock deleted products
    prod1 = MagicMock(spec=Product)
    prod1.id = 1
    prod1.name = "Deleted Prod 1"
    prod1.price = 10.0
    prod2 = MagicMock(spec=Product)
    prod2.id = 2
    prod2.name = "Deleted Prod 2"
    prod2.price = 20.0

    mock_crud.get_deleted_products = AsyncMock(return_value=[prod1, prod2])

    # Ensure get_message returns a string for InlineKeyboardButton validation
    mock_manager.get_message.return_value = "Restore Product"

    # Mock DTO validation to return the mock object itself (duck typing)
    mocker.patch(
        "ecombot.bot.handlers.admin.products.restore.ProductDTO.model_validate",
        side_effect=lambda x: x,
    )

    await restore.restore_product_start(
        query, callback_data, mock_session, callback_message
    )

    mock_crud.get_deleted_products.assert_awaited_once_with(mock_session)
    callback_message.edit_text.assert_awaited_once()
    query.answer.assert_awaited_once()


async def test_restore_product_start_none_found(
    mock_manager, mock_crud, mock_keyboards, mock_session
):
    """Test behavior when no deleted products exist."""
    query = AsyncMock()
    callback_message = AsyncMock()
    callback_data = MagicMock(spec=AdminCallbackFactory)

    mock_crud.get_deleted_products = AsyncMock(return_value=[])

    await restore.restore_product_start(
        query, callback_data, mock_session, callback_message
    )

    callback_message.edit_text.assert_awaited_once()
    mock_manager.get_message.assert_any_call(
        "admin_products", "restore_product_none_found"
    )
    query.answer.assert_awaited_once()


async def test_restore_product_start_error(
    mock_manager, mock_crud, mock_keyboards, mock_session
):
    """Test handling of database errors during fetch."""
    query = AsyncMock()
    callback_message = AsyncMock()
    callback_data = MagicMock(spec=AdminCallbackFactory)

    mock_crud.get_deleted_products.side_effect = Exception("DB Error")

    await restore.restore_product_start(
        query, callback_data, mock_session, callback_message
    )

    callback_message.edit_text.assert_awaited_once()
    mock_manager.get_message.assert_any_call(
        "admin_products", "restore_product_load_error"
    )
    query.answer.assert_awaited_once()


async def test_restore_product_confirm_success(
    mock_manager, mock_crud, mock_keyboards, mock_session
):
    """Test successful restoration of a product."""
    query = AsyncMock()
    callback_message = AsyncMock()
    callback_data = MagicMock(spec=ConfirmationCallbackFactory)
    callback_data.item_id = 1

    mock_crud.restore_product = AsyncMock(return_value=True)

    await restore.restore_product_confirm(
        query, callback_data, mock_session, callback_message
    )

    mock_crud.restore_product.assert_awaited_once_with(mock_session, 1)
    callback_message.edit_text.assert_awaited_once()
    mock_manager.get_message.assert_any_call(
        "admin_products", "restore_product_success"
    )
    query.answer.assert_awaited_once()


async def test_restore_product_confirm_not_found(
    mock_manager, mock_crud, mock_keyboards, mock_session
):
    """Test restoration when product is not found (or already restored)."""
    query = AsyncMock()
    callback_message = AsyncMock()
    callback_data = MagicMock(spec=ConfirmationCallbackFactory)
    callback_data.item_id = 1

    mock_crud.restore_product = AsyncMock(return_value=False)

    await restore.restore_product_confirm(
        query, callback_data, mock_session, callback_message
    )

    callback_message.edit_text.assert_awaited_once()
    mock_manager.get_message.assert_any_call(
        "admin_products", "restore_product_not_found"
    )
    query.answer.assert_awaited_once()


async def test_restore_product_confirm_error(
    mock_manager, mock_crud, mock_keyboards, mock_session
):
    """Test handling of database errors during restoration."""
    query = AsyncMock()
    callback_message = AsyncMock()
    callback_data = MagicMock(spec=ConfirmationCallbackFactory)
    callback_data.item_id = 1

    mock_crud.restore_product.side_effect = Exception("DB Error")

    await restore.restore_product_confirm(
        query, callback_data, mock_session, callback_message
    )

    callback_message.edit_text.assert_awaited_once()
    mock_manager.get_message.assert_any_call(
        "admin_products", "restore_product_unexpected_error"
    )
    query.answer.assert_awaited_once()
