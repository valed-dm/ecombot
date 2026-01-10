"""
Unit tests for catalog keyboards.

This module verifies:
- Generation of category list keyboard.
- Generation of product list keyboard.
- Generation of product details keyboard (add to cart, back navigation).
"""

from unittest.mock import MagicMock

from aiogram.types import InlineKeyboardMarkup
import pytest
from pytest_mock import MockerFixture

from ecombot.bot.callback_data import CartCallbackFactory
from ecombot.bot.callback_data import CatalogCallbackFactory
from ecombot.bot.keyboards import catalog
from ecombot.schemas.dto import CategoryDTO
from ecombot.schemas.dto import ProductDTO


@pytest.fixture
def mock_manager(mocker: MockerFixture):
    """Mocks the central manager to return predictable strings."""
    manager = mocker.patch("ecombot.bot.keyboards.catalog.manager")
    manager.get_message.side_effect = lambda section, key, **kwargs: f"[{key}]"
    return manager


def test_get_catalog_categories_keyboard(mock_manager):
    """Test the categories keyboard."""
    cat1 = MagicMock(spec=CategoryDTO)
    cat1.id = 1
    cat1.name = "Electronics"

    cat2 = MagicMock(spec=CategoryDTO)
    cat2.id = 2
    cat2.name = "Books"

    keyboard = catalog.get_catalog_categories_keyboard([cat1, cat2])

    assert isinstance(keyboard, InlineKeyboardMarkup)

    buttons = [btn for row in keyboard.inline_keyboard for btn in row]
    callbacks = [btn.callback_data for btn in buttons]
    texts = [btn.text for btn in buttons]

    assert "Electronics" in texts
    assert "Books" in texts

    assert CatalogCallbackFactory(action="view_category", item_id=1).pack() in callbacks
    assert CatalogCallbackFactory(action="view_category", item_id=2).pack() in callbacks


def test_get_catalog_products_keyboard(mock_manager):
    """Test the products list keyboard."""
    prod1 = MagicMock(spec=ProductDTO)
    prod1.id = 10
    prod1.name = "Phone"
    prod1.price = 100.0

    keyboard = catalog.get_catalog_products_keyboard([prod1])

    buttons = [btn for row in keyboard.inline_keyboard for btn in row]
    callbacks = [btn.callback_data for btn in buttons]

    # Check product button
    assert CatalogCallbackFactory(action="view_product", item_id=10).pack() in callbacks

    # Check back button
    assert CatalogCallbackFactory(action="back_to_main", item_id=0).pack() in callbacks


def test_get_product_details_keyboard(mock_manager):
    """Test the product details keyboard."""
    product = MagicMock(spec=ProductDTO)
    product.id = 50
    product.category = MagicMock()
    product.category.id = 5

    keyboard = catalog.get_product_details_keyboard(product)

    buttons = [btn for row in keyboard.inline_keyboard for btn in row]
    callbacks = [btn.callback_data for btn in buttons]

    # Check Add to Cart
    assert CartCallbackFactory(action="add", item_id=50).pack() in callbacks

    # Check Back to Products (view_category)
    assert CatalogCallbackFactory(action="view_category", item_id=5).pack() in callbacks
