"""
Unit tests for admin helper functions.

This module verifies the utility functions used across admin handlers, ensuring:
- Product edit menu text is generated correctly.
- Menus are sent correctly (handling image vs text and edit vs new message).
- Photo uploads are processed and saved correctly.
- Admin panel navigation handles message editing failures gracefully.
"""

from pathlib import Path
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import PhotoSize
import pytest
from pytest_mock import MockerFixture

from ecombot.bot.handlers.admin import helpers


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    return mocker.patch("ecombot.bot.handlers.admin.helpers.manager")


@pytest.fixture
def mock_settings(mocker: MockerFixture):
    return mocker.patch("ecombot.bot.handlers.admin.helpers.settings")


@pytest.fixture
def mock_keyboards(mocker: MockerFixture):
    mocker.patch("ecombot.bot.handlers.admin.helpers.get_edit_product_menu_keyboard")
    mocker.patch("ecombot.bot.handlers.admin.helpers.get_admin_panel_keyboard")


def test_get_product_edit_menu_text(mock_manager, mock_settings):
    """Test generating the text for the product edit menu."""
    # Setup
    mock_settings.CURRENCY = "$"

    # Mock manager responses
    admin_manager = MagicMock()
    mock_manager.get_manager.return_value = admin_manager
    admin_manager.get_message.side_effect = lambda key: f"[{key}]"

    product = MagicMock()
    product.name = "Test Product"
    product.description = "Desc"
    product.price = 10.0
    product.stock = 5

    # Execute
    result = helpers.get_product_edit_menu_text(product)

    # Assert
    assert "Test Product" in result
    assert "Desc" in result
    assert "$10.00" in result
    assert "5" in result
    assert "[edit_menu_header]" in result


async def test_send_product_edit_menu_text_only(mock_manager, mock_keyboards):
    """Test sending the edit menu for a product without an image."""
    bot = AsyncMock()
    message = AsyncMock()
    product = MagicMock()
    product.image_url = None
    product.id = 1
    product.category.id = 2
    product.price = 10.0
    product.stock = 5

    await helpers.send_product_edit_menu(bot, 123, message, product, 456, 2)

    message.delete.assert_awaited_once()
    bot.send_message.assert_awaited_once()
    bot.send_photo.assert_not_awaited()


async def test_send_product_edit_menu_with_image_success(
    mock_manager, mock_keyboards, mocker
):
    """Test sending the edit menu for a product with an image."""
    bot = AsyncMock()
    message = AsyncMock()
    product = MagicMock()
    product.image_url = "/path/to/image.jpg"
    product.id = 1
    product.category.id = 2
    product.price = 10.0
    product.stock = 5

    # Mock FSInputFile since it's instantiated inside the function
    mocker.patch("aiogram.types.FSInputFile")

    await helpers.send_product_edit_menu(bot, 123, message, product, 456, 2)

    message.delete.assert_awaited_once()
    bot.send_photo.assert_awaited_once()
    bot.send_message.assert_not_awaited()


async def test_send_product_edit_menu_with_image_failure(
    mock_manager, mock_keyboards, mocker
):
    """Test fallback to text message if sending photo fails."""
    bot = AsyncMock()
    message = AsyncMock()
    product = MagicMock()
    product.image_url = "/path/to/image.jpg"
    product.id = 1
    product.category.id = 2
    product.price = 10.0
    product.stock = 5

    mocker.patch("aiogram.types.FSInputFile")
    # Simulate send_photo failing (e.g. file not found or bad request)
    bot.send_photo.side_effect = TelegramBadRequest(method="sendPhoto", message="Error")

    await helpers.send_product_edit_menu(bot, 123, message, product, 456, 2)

    message.delete.assert_awaited_once()
    bot.send_photo.assert_awaited_once()
    # Should fallback to send_message
    bot.send_message.assert_awaited_once()


async def test_send_main_admin_panel_edit_success(mock_manager, mock_keyboards):
    """Test successfully editing the message to show admin panel."""
    message = AsyncMock()

    await helpers.send_main_admin_panel(message)

    message.edit_text.assert_awaited_once()
    message.answer.assert_not_awaited()


async def test_send_main_admin_panel_edit_fail(mock_manager, mock_keyboards):
    """Test fallback to sending new message if editing fails."""
    message = AsyncMock()
    message.edit_text.side_effect = TelegramBadRequest(method="edit", message="Error")

    await helpers.send_main_admin_panel(message)

    message.edit_text.assert_awaited_once()
    message.answer.assert_awaited_once()


async def test_process_photo_upload_success(mock_settings):
    """Test successful photo download."""
    bot = AsyncMock()
    photo = MagicMock(spec=PhotoSize)
    photo.file_id = "file_123"

    mock_settings.PRODUCT_IMAGE_DIR = MagicMock()
    mock_settings.PRODUCT_IMAGE_DIR.__truediv__.return_value = Path("/tmp/img.jpg")

    result = await helpers.process_photo_upload(bot, photo, 1)

    bot.download.assert_awaited_once()
    assert result == "/tmp/img.jpg"


async def test_process_photo_upload_failure(mock_settings):
    """Test handling of photo download failure."""
    bot = AsyncMock()
    photo = MagicMock(spec=PhotoSize)

    mock_settings.PRODUCT_IMAGE_DIR = MagicMock()
    # Simulate error during download
    bot.download.side_effect = Exception("Download failed")

    result = await helpers.process_photo_upload(bot, photo, 1)

    assert result is None


async def test_update_product_menu_failure(mock_manager, mock_keyboards, mock_settings):
    """Test fallback when updating product menu fails."""
    bot = AsyncMock()
    message = AsyncMock()
    message.chat.id = 123
    product = MagicMock()
    product.price = 10.0
    product.stock = 5

    bot.edit_message_text.side_effect = TelegramBadRequest(
        method="edit", message="Error"
    )

    await helpers.update_product_menu(bot, message, product, 456)

    bot.edit_message_text.assert_awaited_once()
    message.answer.assert_awaited_once()
