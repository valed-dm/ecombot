"""Cart-related keyboards."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ecombot.schemas.dto import CartDTO

from ..callback_data import CartCallbackFactory, CatalogCallbackFactory


def get_cart_keyboard(cart: CartDTO) -> InlineKeyboardMarkup:
    """
    Builds an interactive keyboard for the shopping cart.
    Features a compact, single-row design for item actions.
    """
    builder = InlineKeyboardBuilder()

    for item in cart.items:
        builder.row(
            InlineKeyboardButton(
                text="➖",
                callback_data=CartCallbackFactory(
                    action="decrease", item_id=item.id
                ).pack(),
            ),
            InlineKeyboardButton(
                text=f"{item.quantity}",
                callback_data=f"quantity_{item.id}",
            ),
            InlineKeyboardButton(
                text=f"{item.product.name}",
                callback_data=CatalogCallbackFactory(
                    action="view_product", item_id=item.product.id
                ).pack(),
            ),
            InlineKeyboardButton(
                text="➕",
                callback_data=CartCallbackFactory(
                    action="increase", item_id=item.id
                ).pack(),
            ),
            InlineKeyboardButton(
                text="❌",
                callback_data=CartCallbackFactory(
                    action="remove", item_id=item.id
                ).pack(),
            ),
        )

    action_buttons = []
    if cart.items:
        action_buttons.append(
            InlineKeyboardButton(text="✅ Checkout", callback_data="checkout_start")
        )
    action_buttons.append(
        InlineKeyboardButton(
            text="🛍️ Catalog",
            callback_data=CatalogCallbackFactory(
                action="back_to_main", item_id=0
            ).pack(),
        )
    )
    builder.row(*action_buttons)

    return builder.as_markup()