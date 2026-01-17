"""
Unit tests for the 'Add Product' admin handler.

This module verifies the FSM flow for adding new products, ensuring that:
- The process starts correctly and handles category loading.
- All input fields (name, description, price, stock) are validated.
- Image uploading works correctly, including the skip option.
- The product is successfully created in the database via the service layer.
- Error handling works, including cleaning up uploaded files if creation fails.
"""

from decimal import Decimal
from pathlib import Path
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
import pytest
from pytest_mock import MockerFixture

from ecombot.bot.callback_data import AdminCallbackFactory
from ecombot.bot.callback_data import CatalogCallbackFactory
from ecombot.bot.handlers.admin.products import add
from ecombot.bot.handlers.admin.products.states import AddProduct
from ecombot.db.models import Category


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager used for retrieving messages."""
    return mocker.patch("ecombot.bot.handlers.admin.products.add.manager")


@pytest.fixture
def mock_catalog_service(mocker: MockerFixture):
    """Mocks the catalog service."""
    return mocker.patch("ecombot.bot.handlers.admin.products.add.catalog_service")


@pytest.fixture
def mock_settings(mocker: MockerFixture):
    """Mocks the settings configuration."""
    return mocker.patch("ecombot.bot.handlers.admin.products.add.settings")


async def test_add_product_start_success(
    mock_manager, mock_catalog_service, mock_session
):
    """Test starting the add product flow with available categories."""
    # Setup query with a valid Message object for isinstance checks
    query = MagicMock(spec=CallbackQuery)
    query.message = MagicMock(spec=Message)
    query.message.edit_text = AsyncMock()
    query.answer = AsyncMock()

    state = AsyncMock(spec=FSMContext)
    callback_data = MagicMock(spec=AdminCallbackFactory)

    # Ensure get_message returns a string for message editing
    mock_manager.get_message.return_value = "Choose category"

    # Ensure category has a string name for the keyboard button
    cat = MagicMock(spec=Category)
    cat.name = "Test Category"
    mock_catalog_service.get_all_categories = AsyncMock(return_value=[cat])
    await add.add_product_start(query, mock_session, state, callback_data)

    query.message.edit_text.assert_awaited_once()
    state.set_state.assert_awaited_once_with(AddProduct.choose_category)
    query.answer.assert_awaited_once()


async def test_add_product_start_no_categories(
    mock_manager, mock_catalog_service, mock_session
):
    """Test starting the flow when no categories exist."""
    query = MagicMock(spec=CallbackQuery)
    query.message = MagicMock(spec=Message)
    query.message.edit_text = AsyncMock()
    query.answer = AsyncMock()

    state = AsyncMock(spec=FSMContext)
    callback_data = MagicMock(spec=AdminCallbackFactory)

    mock_catalog_service.get_all_categories = AsyncMock(return_value=[])

    await add.add_product_start(query, mock_session, state, callback_data)

    query.message.edit_text.assert_awaited_once()
    # Should not advance state
    state.set_state.assert_not_awaited()
    query.answer.assert_awaited_once()


async def test_add_product_choose_category(mock_manager):
    """Test selecting a category."""
    query = AsyncMock()
    callback_message = AsyncMock()
    state = AsyncMock()
    callback_data = MagicMock(spec=CatalogCallbackFactory)
    callback_data.item_id = 1

    await add.add_product_choose_category(query, callback_data, state, callback_message)

    state.update_data.assert_awaited_once_with(category_id=1)
    callback_message.edit_text.assert_awaited_once()
    state.set_state.assert_awaited_once_with(AddProduct.name)


async def test_add_product_name_valid(mock_manager):
    """Test providing a valid product name."""
    message = AsyncMock()
    message.text = "Product Name"
    state = AsyncMock()

    await add.add_product_name(message, state)

    state.update_data.assert_awaited_once_with(name="Product Name")
    state.set_state.assert_awaited_once_with(AddProduct.description)


async def test_add_product_description_valid(mock_manager):
    """Test providing a valid description."""
    message = AsyncMock()
    message.text = "Description"
    state = AsyncMock()

    await add.add_product_description_step(message, state)

    state.update_data.assert_awaited_once_with(description="Description")
    state.set_state.assert_awaited_once_with(AddProduct.price)


async def test_add_product_price_valid(mock_manager):
    """Test providing a valid price."""
    message = AsyncMock()
    message.text = "10.50"
    state = AsyncMock()

    await add.add_product_price_step(message, state)

    state.update_data.assert_awaited_once_with(price=Decimal("10.50"))
    state.set_state.assert_awaited_once_with(AddProduct.stock)


async def test_add_product_price_invalid(mock_manager):
    """Test providing an invalid price format."""
    message = AsyncMock()
    message.text = "abc"
    state = AsyncMock()

    await add.add_product_price_step(message, state)

    state.update_data.assert_not_awaited()
    message.answer.assert_awaited()  # Error message


async def test_add_product_stock_valid(mock_manager):
    """Test providing a valid stock quantity."""
    message = AsyncMock()
    message.text = "100"
    state = AsyncMock()

    await add.add_product_stock_step(message, state)

    state.update_data.assert_awaited_once_with(stock=100)
    state.set_state.assert_awaited_once_with(AddProduct.get_image)


async def test_add_product_get_image_skip(
    mock_manager, mock_catalog_service, mock_session
):
    """Test skipping image upload."""
    message = AsyncMock()
    message.photo = None  # Simulate skip command or no photo
    state = AsyncMock()
    bot = AsyncMock()

    state.get_data.return_value = {
        "name": "P1",
        "description": "D1",
        "price": Decimal("10"),
        "stock": 5,
        "category_id": 1,
        "image_url": None,
    }
    mock_catalog_service.add_new_product = AsyncMock(return_value=MagicMock(name="P1"))

    await add.add_product_get_image(message, state, mock_session, bot)

    state.update_data.assert_awaited_once_with(image_url=None)
    mock_catalog_service.add_new_product.assert_awaited_once()
    state.clear.assert_awaited_once()


async def test_add_product_get_image_upload(
    mock_manager, mock_catalog_service, mock_session, mock_settings
):
    """Test uploading a product image."""
    message = AsyncMock()
    photo_size = MagicMock()
    photo_size.file_id = "file_123"
    message.photo = [photo_size]
    state = AsyncMock()
    bot = AsyncMock()

    state.get_data.return_value = {
        "name": "P1",
        "description": "D1",
        "price": Decimal("10"),
        "stock": 5,
        "category_id": 1,
        "image_url": "/tmp/img.jpg",
    }
    mock_catalog_service.add_new_product = AsyncMock(return_value=MagicMock(name="P1"))

    # Mock Path mkdir and path construction
    mock_settings.PRODUCT_IMAGE_DIR = MagicMock()
    mock_settings.PRODUCT_IMAGE_DIR.__truediv__.return_value = Path("/tmp/img.jpg")

    await add.add_product_get_image(message, state, mock_session, bot)

    bot.download.assert_awaited_once()
    mock_catalog_service.add_new_product.assert_awaited_once()

    # Verify image_url passed to service is the string path
    call_kwargs = mock_catalog_service.add_new_product.call_args.kwargs
    assert call_kwargs["image_url"] == "/tmp/img.jpg"


async def test_add_product_creation_error_cleanup(
    mock_manager, mock_catalog_service, mock_session, mock_settings, mocker
):
    """
    Test that the uploaded image file is deleted if product creation fails.
    """
    message = AsyncMock()
    photo_size = MagicMock()
    message.photo = [photo_size]
    state = AsyncMock()
    bot = AsyncMock()

    state.get_data.return_value = {
        "name": "P1",
        "description": "D1",
        "price": Decimal("10"),
        "stock": 5,
        "category_id": 1,
        "image_url": "/tmp/img.jpg",
    }

    # Simulate service error
    mock_catalog_service.add_new_product.side_effect = Exception("DB Error")

    # Mock file system operations
    mock_path_obj = MagicMock()
    mocker.patch(
        "ecombot.bot.handlers.admin.products.add.Path", return_value=mock_path_obj
    )

    mock_settings.PRODUCT_IMAGE_DIR = MagicMock()
    mock_settings.PRODUCT_IMAGE_DIR.__truediv__.return_value = Path("/tmp/img.jpg")

    await add.add_product_get_image(message, state, mock_session, bot)

    # Verify cleanup was attempted
    mock_path_obj.unlink.assert_called_once()
    message.answer.assert_awaited()  # Error message
    state.clear.assert_awaited_once()
