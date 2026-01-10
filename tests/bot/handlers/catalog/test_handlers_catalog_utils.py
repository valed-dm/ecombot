"""
Unit tests for catalog utilities.

This module verifies:
- Displaying the main catalog (new message vs edit).
- Handling transitions between photo and text messages.
- Sending product details with optional photo support.
"""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from aiogram.types import Message
import pytest
from pytest_mock import MockerFixture

from ecombot.bot.handlers.catalog import utils
from ecombot.schemas.dto import ProductDTO


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager."""
    manager = mocker.patch("ecombot.bot.handlers.catalog.utils.manager")
    manager.get_message.return_value = "Message text"
    return manager


@pytest.fixture
def mock_catalog_service(mocker: MockerFixture):
    """Mocks the catalog service."""
    return mocker.patch("ecombot.bot.handlers.catalog.utils.catalog_service")


@pytest.fixture
def mock_keyboards(mocker: MockerFixture):
    """Mocks the keyboard generators."""
    mocker.patch("ecombot.bot.handlers.catalog.utils.get_catalog_categories_keyboard")
    mocker.patch("ecombot.bot.handlers.catalog.utils.get_product_details_keyboard")


async def test_show_main_catalog_new_message(
    mock_manager, mock_catalog_service, mock_keyboards, mock_session
):
    """Test showing catalog as a new message."""
    # spec=Message is required for isinstance check in the function
    message = AsyncMock(spec=Message)
    message.answer = AsyncMock()
    message.edit_text = AsyncMock()
    mock_catalog_service.get_all_categories = AsyncMock(return_value=[])

    await utils.show_main_catalog(message, mock_session, is_edit=False)

    message.answer.assert_awaited_once()
    message.edit_text.assert_not_awaited()


async def test_show_main_catalog_edit_message(
    mock_manager, mock_catalog_service, mock_keyboards, mock_session
):
    """Test showing catalog by editing existing message."""
    message = AsyncMock(spec=Message)
    message.edit_text = AsyncMock()
    message.answer = AsyncMock()
    mock_catalog_service.get_all_categories = AsyncMock(return_value=[])

    await utils.show_main_catalog(message, mock_session, is_edit=True)

    message.edit_text.assert_awaited_once()
    message.answer.assert_not_awaited()


async def test_handle_message_with_photo_transition_has_photo(mock_manager):
    """Test transition when original message has a photo."""
    message = AsyncMock()
    message.photo = [MagicMock()]  # Simulate photo presence
    message.chat.id = 123
    bot = AsyncMock()

    await utils.handle_message_with_photo_transition(message, bot, "text", "keyboard")

    message.delete.assert_awaited_once()
    bot.send_message.assert_awaited_once_with(
        chat_id=123, text="text", reply_markup="keyboard"
    )
    message.edit_text.assert_not_awaited()


async def test_handle_message_with_photo_transition_no_photo(mock_manager):
    """Test transition when original message is text-only."""
    message = AsyncMock()
    message.photo = None
    bot = AsyncMock()

    await utils.handle_message_with_photo_transition(message, bot, "text", "keyboard")

    message.edit_text.assert_awaited_once_with("text", reply_markup="keyboard")
    message.delete.assert_not_awaited()
    bot.send_message.assert_not_awaited()


async def test_send_product_with_photo_success(mock_manager, mock_keyboards, mocker):
    """Test sending product with a valid photo."""
    message = AsyncMock()
    message.chat.id = 123
    bot = AsyncMock()

    product = MagicMock(spec=ProductDTO)
    product.id = 1
    product.name = "Test Product"
    product.description = "Test Description"
    product.price = 10.0
    product.image_url = "/path/to/image.jpg"

    mocker.patch("ecombot.bot.handlers.catalog.utils.FSInputFile")

    await utils.send_product_with_photo(message, bot, product)

    bot.send_photo.assert_awaited_once()
    message.delete.assert_awaited_once()
    message.edit_text.assert_not_awaited()


async def test_send_product_with_photo_failure_fallback(
    mock_manager, mock_keyboards, mocker
):
    """Test fallback to text if sending photo fails."""
    message = AsyncMock()
    bot = AsyncMock()

    product = MagicMock(spec=ProductDTO)
    product.id = 1
    product.name = "Test Product"
    product.description = "Test Description"
    product.price = 10.0
    product.image_url = "/path/to/image.jpg"

    mocker.patch("ecombot.bot.handlers.catalog.utils.FSInputFile")
    bot.send_photo.side_effect = Exception("File not found")

    await utils.send_product_with_photo(message, bot, product)

    bot.send_photo.assert_awaited_once()
    message.delete.assert_not_awaited()
    message.edit_text.assert_awaited_once()
