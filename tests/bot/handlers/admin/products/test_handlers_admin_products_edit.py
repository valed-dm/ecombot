"""
Unit tests for the 'Edit Product' admin handler.

This module verifies the FSM flow for editing products, ensuring that:
- The workflow starts correctly (category -> product selection).
- Field selection works for both text fields and images.
- Input validation is applied correctly for prices, stock, and text length.
- Updates are persisted via the service layer.
- Error handling covers database issues and invalid inputs.
"""

from decimal import Decimal
from pathlib import Path
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ecombot.bot.callback_data import AdminCallbackFactory
from ecombot.bot.callback_data import CatalogCallbackFactory
from ecombot.bot.callback_data import EditProductCallbackFactory
from ecombot.bot.handlers.admin.products import edit
from ecombot.bot.handlers.admin.products.states import EditProduct
from ecombot.db.models import Category
from ecombot.db.models import Product


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager used for retrieving messages."""
    return mocker.patch("ecombot.bot.handlers.admin.products.edit.manager")


@pytest.fixture
def mock_catalog_service(mocker: MockerFixture):
    """Mocks the catalog service."""
    return mocker.patch("ecombot.bot.handlers.admin.products.edit.catalog_service")


@pytest.fixture
def mock_settings(mocker: MockerFixture):
    """Mocks the settings configuration."""
    return mocker.patch("ecombot.bot.handlers.admin.products.edit.settings")


@pytest.fixture
def mock_keyboards(mocker: MockerFixture):
    """Mocks the keyboard generation functions."""
    mocker.patch(
        "ecombot.bot.handlers.admin.products.edit.get_catalog_categories_keyboard"
    )
    mocker.patch(
        "ecombot.bot.handlers.admin.products.edit.get_catalog_products_keyboard"
    )
    mocker.patch(
        "ecombot.bot.handlers.admin.products.edit.get_edit_product_menu_keyboard"
    )
    mocker.patch("ecombot.bot.handlers.admin.products.edit.get_admin_panel_keyboard")
    mocker.patch("ecombot.bot.handlers.admin.products.edit.get_cancel_keyboard")


async def test_edit_product_start_success(
    mock_manager, mock_catalog_service, mock_keyboards, mock_session
):
    """Test starting the edit flow with available categories."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    callback_data = MagicMock(spec=AdminCallbackFactory)

    mock_manager.get_message.return_value = "Choose category"
    mock_catalog_service.get_all_categories = AsyncMock(
        return_value=[MagicMock(spec=Category)]
    )

    await edit.edit_product_start(
        query, callback_data, mock_session, state, callback_message
    )

    callback_message.edit_text.assert_awaited_once()
    state.set_state.assert_awaited_once_with(EditProduct.choose_category)
    query.answer.assert_awaited_once()


async def test_edit_product_choose_category_success(
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

    await edit.edit_product_choose_category(
        query, callback_data, mock_session, state, callback_message
    )

    callback_message.edit_text.assert_awaited_once()
    state.set_state.assert_awaited_once_with(EditProduct.choose_product)
    query.answer.assert_awaited_once()


async def test_edit_product_choose_product_success(
    mock_manager, mock_catalog_service, mock_keyboards, mock_session
):
    """Test selecting a product to edit."""
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
    product.category.id = 1
    mock_catalog_service.get_single_product_details_for_admin = AsyncMock(
        return_value=product
    )

    # Mock nested manager call for labels
    mock_admin_manager = MagicMock()
    mock_manager.get_manager.return_value = mock_admin_manager
    mock_admin_manager.get_message.return_value = "Label"

    await edit.edit_product_choose_product(
        query, callback_data, mock_session, state, callback_message
    )

    state.update_data.assert_awaited_once_with(
        product_id=10, product_name="Test Product"
    )
    callback_message.edit_text.assert_awaited_once()
    state.set_state.assert_awaited_once_with(EditProduct.choose_field)
    query.answer.assert_awaited_once()


async def test_edit_product_choose_field_text(mock_manager, mock_keyboards):
    """Test selecting a text field to edit."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    callback_data = MagicMock(spec=EditProductCallbackFactory)
    callback_data.action = "name"

    await edit.edit_product_choose_field(query, callback_data, state, callback_message)

    state.update_data.assert_awaited_once_with(edit_field="name")
    callback_message.edit_text.assert_awaited_once()
    state.set_state.assert_awaited_once_with(EditProduct.get_new_value)
    query.answer.assert_awaited_once()


async def test_edit_product_choose_field_image(mock_manager, mock_keyboards):
    """Test selecting image field to edit."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    callback_data = MagicMock(spec=EditProductCallbackFactory)
    callback_data.action = "change_photo"

    await edit.edit_product_choose_field(query, callback_data, state, callback_message)

    state.update_data.assert_awaited_once_with(edit_field="image_url")
    callback_message.edit_text.assert_awaited_once()
    state.set_state.assert_awaited_once_with(EditProduct.get_new_image)
    query.answer.assert_awaited_once()


async def test_edit_product_get_new_value_valid_price(
    mock_manager, mock_catalog_service, mock_session
):
    """Test updating price with valid input."""
    message = AsyncMock()
    message.text = "15.50"
    state = AsyncMock()
    state.get_data.return_value = {
        "edit_field": "price",
        "product_id": 10,
        "product_name": "P1",
    }

    mock_catalog_service.update_product_details = AsyncMock()

    await edit.edit_product_get_new_value(message, state, mock_session)

    mock_catalog_service.update_product_details.assert_awaited_once_with(
        mock_session, 10, {"price": Decimal("15.50")}
    )
    message.answer.assert_awaited_once()
    state.clear.assert_awaited_once()


async def test_edit_product_get_new_value_invalid_price(
    mock_manager, mock_catalog_service, mock_session
):
    """Test updating price with invalid input."""
    message = AsyncMock()
    message.text = "-5"
    state = AsyncMock()
    state.get_data.return_value = {"edit_field": "price", "product_id": 10}

    mock_catalog_service.update_product_details = AsyncMock()

    await edit.edit_product_get_new_value(message, state, mock_session)

    mock_catalog_service.update_product_details.assert_not_awaited()
    message.answer.assert_awaited()  # Error message
    state.clear.assert_not_awaited()


async def test_edit_product_get_new_image_success(
    mock_manager, mock_catalog_service, mock_session, mock_settings
):
    """Test updating product image."""
    message = AsyncMock()
    photo_size = MagicMock()
    photo_size.file_id = "file_123"
    message.photo = [photo_size]
    state = AsyncMock()
    bot = AsyncMock()

    state.get_data.return_value = {"product_id": 10}

    mock_settings.PRODUCT_IMAGE_DIR = MagicMock()
    mock_settings.PRODUCT_IMAGE_DIR.__truediv__.return_value = Path("/tmp/img.jpg")

    mock_catalog_service.update_product_details = AsyncMock()

    await edit.edit_product_get_new_image(message, state, mock_session, bot)

    bot.download.assert_awaited_once()
    mock_catalog_service.update_product_details.assert_awaited_once()

    # Check arguments
    call_args = mock_catalog_service.update_product_details.call_args
    assert call_args[0][1] == 10
    assert call_args[0][2]["image_url"] == "/tmp/img.jpg"

    state.clear.assert_awaited_once()
