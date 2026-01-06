"""Order-related keyboards."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ecombot.core.manager import central_manager as manager
from ecombot.schemas.dto import OrderDTO

from ..callback_data import CatalogCallbackFactory
from ..callback_data import OrderCallbackFactory


def get_orders_list_keyboard(orders: list[OrderDTO]) -> InlineKeyboardMarkup:
    """
    Builds a keyboard for the order history list, with a 'View Details'
    button for each.
    """
    builder = InlineKeyboardBuilder()

    if not orders:
        builder.button(
            text=manager.get_message("keyboards", "go_to_catalog"),
            callback_data=CatalogCallbackFactory(action="back_to_main", item_id=0),
        )
    else:
        for order in orders:
            builder.button(
                text=f"🔎 View Order #{order.order_number}",
                callback_data=OrderCallbackFactory(
                    action="view_details", item_id=order.id
                ),
            )

    builder.adjust(1)
    return builder.as_markup()


def get_order_details_keyboard() -> InlineKeyboardMarkup:
    """Builds a simple keyboard with a 'Back to Orders' button."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⬅️ Back to Order History",
        callback_data=OrderCallbackFactory(action="back_to_list"),
    )
    return builder.as_markup()
