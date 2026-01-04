"""Catalog-related keyboards."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ecombot.schemas.dto import CategoryDTO, ProductDTO

from ..callback_data import CatalogCallbackFactory, CartCallbackFactory


def get_catalog_categories_keyboard(
    categories: list[CategoryDTO],
) -> InlineKeyboardMarkup:
    """Builds a keyboard for the top-level categories."""
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(
            text=category.name,
            callback_data=CatalogCallbackFactory(
                action="view_category", item_id=category.id
            ),
        )
    builder.adjust(3)
    return builder.as_markup()


def get_catalog_products_keyboard(products: list[ProductDTO]) -> InlineKeyboardMarkup:
    """Builds a keyboard for the list of products in a category."""
    builder = InlineKeyboardBuilder()
    for product in products:
        builder.button(
            text=f"{product.name} - ${product.price:.2f}",
            callback_data=CatalogCallbackFactory(
                action="view_product", item_id=product.id
            ),
        )
    builder.button(
        text="⬅️ Back to Categories",
        callback_data=CatalogCallbackFactory(action="back_to_main", item_id=0),
    )
    builder.adjust(1)
    return builder.as_markup()


def get_product_details_keyboard(product: ProductDTO) -> InlineKeyboardMarkup:
    """Builds a keyboard for a single product view."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="➕ Add to Cart",
        callback_data=CartCallbackFactory(action="add", item_id=product.id),
    )
    builder.button(
        text="⬅️ Back to Products",
        callback_data=CatalogCallbackFactory(
            action="view_category", item_id=product.category.id
        ),
    )
    return builder.as_markup()