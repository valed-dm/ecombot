"""
Unit tests for the 'Delete Product' admin handler.

This module verifies the FSM flow for deleting products, ensuring that:
- The product deletion workflow starts correctly (category selection).
- Product selection works and handles empty/error states.
- Confirmation logic handles success, cancellation, and errors.
- Service layer interactions are correct.
"""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ecombot.bot.callback_data import AdminCallbackFactory
from ecombot.bot.callback_data import CatalogCallbackFactory
from ecombot.bot.callback_data import ConfirmationCallbackFactory
from ecombot.bot.handlers.admin.products import delete
from ecombot.bot.handlers.admin.states import DeleteProduct
from ecombot.db.models import Category
from ecombot.db.models import Product


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager used for retrieving messages."""
    return mocker.patch("ecombot.bot.handlers.admin.products.delete.manager")


@pytest.fixture
def mock_catalog_service(mocker: MockerFixture):
    """Mocks the catalog service."""
    return mocker.patch("ecombot.bot.handlers.admin.products.delete.catalog_service")


@pytest.fixture
def mock_keyboards(mocker: MockerFixture):
    """Mocks the keyboard generation functions."""
    mocker.patch(
        "ecombot.bot.handlers.admin.products.delete.get_catalog_categories_keyboard"
    )
    mocker.patch(
        "ecombot.bot.handlers.admin.products.delete.get_catalog_products_keyboard"
    )
    mocker.patch(
        "ecombot.bot.handlers.admin.products.delete.get_delete_confirmation_keyboard"
    )
    mocker.patch("ecombot.bot.handlers.admin.products.delete.get_admin_panel_keyboard")


async def test_delete_product_start_success(
    mock_manager, mock_catalog_service, mock_keyboards, mock_session
):
    """Test starting the delete flow with available categories."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    callback_data = MagicMock(spec=AdminCallbackFactory)

    # Ensure get_message returns a string
    mock_manager.get_message.return_value = "Choose category"

    mock_catalog_service.get_all_categories = AsyncMock(
        return_value=[MagicMock(spec=Category)]
    )

    await delete.delete_product_start(
        query, callback_data, mock_session, state, callback_message
    )

    callback_message.edit_text.assert_awaited_once()
    state.set_state.assert_awaited_once_with(DeleteProduct.choose_category)
    query.answer.assert_awaited_once()


async def test_delete_product_start_no_categories(
    mock_manager, mock_catalog_service, mock_keyboards, mock_session
):
    """Test starting the delete flow when no categories exist."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    callback_data = MagicMock(spec=AdminCallbackFactory)

    mock_catalog_service.get_all_categories = AsyncMock(return_value=[])

    await delete.delete_product_start(
        query, callback_data, mock_session, state, callback_message
    )

    callback_message.edit_text.assert_awaited_once()
    state.set_state.assert_not_awaited()
    query.answer.assert_awaited_once()


async def test_delete_product_choose_category_success(
    mock_manager, mock_catalog_service, mock_keyboards, mock_session
):
    """Test selecting a category with products."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    callback_data = MagicMock(spec=CatalogCallbackFactory)
    callback_data.item_id = 1

    mock_catalog_service.get_products_in_category = AsyncMock(
        return_value=[MagicMock(spec=Product)]
    )

    await delete.delete_product_choose_category(
        query, callback_data, mock_session, state, callback_message
    )

    callback_message.edit_text.assert_awaited_once()
    state.set_state.assert_awaited_once_with(DeleteProduct.choose_product)
    query.answer.assert_awaited_once()


async def test_delete_product_choose_category_no_products(
    mock_manager, mock_catalog_service, mock_keyboards, mock_session
):
    """Test selecting a category with no products."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    callback_data = MagicMock(spec=CatalogCallbackFactory)
    callback_data.item_id = 1

    mock_catalog_service.get_products_in_category = AsyncMock(return_value=[])

    await delete.delete_product_choose_category(
        query, callback_data, mock_session, state, callback_message
    )

    callback_message.edit_text.assert_awaited_once()
    state.clear.assert_awaited_once()
    query.answer.assert_awaited_once()


async def test_delete_product_choose_product_success(
    mock_manager, mock_catalog_service, mock_keyboards, mock_session
):
    """Test selecting a product for deletion."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    callback_data = MagicMock(spec=CatalogCallbackFactory)
    callback_data.item_id = 10

    product = MagicMock(spec=Product)
    product.name = "Test Product"
    product.description = "Desc"
    product.price = 100
    product.stock = 10
    mock_catalog_service.get_single_product_details_for_admin = AsyncMock(
        return_value=product
    )

    # Ensure format string works
    mock_manager.get_message.return_value = "{product_name}"

    await delete.delete_product_choose_product(
        query, callback_data, mock_session, state, callback_message
    )

    state.update_data.assert_awaited_once_with(
        product_id=10, product_name="Test Product"
    )
    callback_message.edit_text.assert_awaited_once()
    state.set_state.assert_awaited_once_with(DeleteProduct.confirm_deletion)
    query.answer.assert_awaited_once()


async def test_delete_product_choose_product_not_found(
    mock_manager, mock_catalog_service, mock_keyboards, mock_session
):
    """Test selecting a product that doesn't exist."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    callback_data = MagicMock(spec=CatalogCallbackFactory)
    callback_data.item_id = 10

    mock_catalog_service.get_single_product_details_for_admin = AsyncMock(
        return_value=None
    )

    await delete.delete_product_choose_product(
        query, callback_data, mock_session, state, callback_message
    )

    callback_message.edit_text.assert_awaited_once()
    state.clear.assert_awaited_once()
    query.answer.assert_awaited_once()


async def test_delete_product_final_confirmed_success(
    mock_manager, mock_catalog_service, mock_keyboards, mock_session
):
    """Test confirming product deletion."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    callback_data = MagicMock(spec=ConfirmationCallbackFactory)
    callback_data.confirm = True
    callback_data.item_id = 10

    state.get_data.return_value = {"product_name": "Test Product"}
    mock_catalog_service.delete_product_by_id = AsyncMock(return_value=True)

    # Ensure format string works
    mock_manager.get_message.return_value = "{product_name}"

    await delete.delete_product_final(
        query, callback_data, mock_session, state, callback_message
    )

    mock_catalog_service.delete_product_by_id.assert_awaited_once_with(mock_session, 10)
    callback_message.edit_text.assert_awaited_once()
    state.clear.assert_awaited_once()
    query.answer.assert_awaited_once()


async def test_delete_product_final_cancelled(
    mock_manager, mock_keyboards, mock_session
):
    """Test cancelling product deletion."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    callback_data = MagicMock(spec=ConfirmationCallbackFactory)
    callback_data.confirm = False

    await delete.delete_product_final(
        query, callback_data, mock_session, state, callback_message
    )

    callback_message.edit_text.assert_awaited_once()
    state.clear.assert_awaited_once()
    query.answer.assert_awaited_once()
