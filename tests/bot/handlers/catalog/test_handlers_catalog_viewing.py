"""
Unit tests for catalog viewing handlers.

This module verifies:
- Viewing products in a category (fetching, keyboard generation, message transition).
- Viewing specific product details (fetching, photo sending, error handling).
"""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ecombot.bot.callback_data import CatalogCallbackFactory
from ecombot.bot.handlers.catalog import viewing
from ecombot.schemas.dto import ProductDTO


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager."""
    manager = mocker.patch("ecombot.bot.handlers.catalog.viewing.manager")
    manager.get_message.return_value = "Message text"
    return manager


@pytest.fixture
def mock_catalog_service(mocker: MockerFixture):
    """Mocks the catalog service."""
    return mocker.patch("ecombot.bot.handlers.catalog.viewing.catalog_service")


@pytest.fixture
def mock_keyboards(mocker: MockerFixture):
    """Mocks the keyboard generators."""
    return mocker.patch(
        "ecombot.bot.handlers.catalog.viewing.get_catalog_products_keyboard"
    )


async def test_view_category_handler(
    mock_manager,
    mock_catalog_service,
    mock_keyboards,
    mock_session,
    mocker,
):
    """Test viewing products in a category."""
    query = AsyncMock()
    callback_message = AsyncMock()
    bot = AsyncMock()
    callback_data = CatalogCallbackFactory(action="view_category", item_id=1)

    mock_products = [MagicMock(spec=ProductDTO)]
    mock_catalog_service.get_products_in_category = AsyncMock(
        return_value=mock_products
    )

    mock_handle_transition = mocker.patch(
        "ecombot.bot.handlers.catalog.viewing.handle_message_with_photo_transition",
        new_callable=AsyncMock,
    )

    await viewing.view_category_handler(
        query, callback_data, mock_session, callback_message, bot
    )

    mock_catalog_service.get_products_in_category.assert_awaited_once_with(
        mock_session, 1
    )
    mock_keyboards.assert_called_once_with(mock_products)
    mock_handle_transition.assert_awaited_once()
    query.answer.assert_awaited_once()


async def test_view_product_handler_success(
    mock_manager, mock_catalog_service, mock_session, mocker
):
    """Test viewing a specific product successfully."""
    query = AsyncMock()
    callback_message = AsyncMock()
    bot = AsyncMock()
    callback_data = CatalogCallbackFactory(action="view_product", item_id=10)

    mock_product = MagicMock(spec=ProductDTO)
    mock_catalog_service.get_single_product_details = AsyncMock(
        return_value=mock_product
    )

    mock_send_photo = mocker.patch(
        "ecombot.bot.handlers.catalog.viewing.send_product_with_photo",
        new_callable=AsyncMock,
    )

    await viewing.view_product_handler(
        query, callback_data, mock_session, callback_message, bot
    )

    mock_catalog_service.get_single_product_details.assert_awaited_once_with(
        mock_session, 10
    )
    mock_send_photo.assert_awaited_once_with(callback_message, bot, mock_product)
    query.answer.assert_awaited_once()


async def test_view_product_handler_not_found(
    mock_manager, mock_catalog_service, mock_session, mocker
):
    """Test viewing a product that doesn't exist."""
    query = AsyncMock()
    callback_message = AsyncMock()
    bot = AsyncMock()
    callback_data = CatalogCallbackFactory(action="view_product", item_id=999)

    mock_catalog_service.get_single_product_details = AsyncMock(return_value=None)

    mock_send_photo = mocker.patch(
        "ecombot.bot.handlers.catalog.viewing.send_product_with_photo",
        new_callable=AsyncMock,
    )

    await viewing.view_product_handler(
        query, callback_data, mock_session, callback_message, bot
    )

    mock_send_photo.assert_not_awaited()
    query.answer.assert_awaited_once()
    assert query.answer.call_args[1].get("show_alert") is True
