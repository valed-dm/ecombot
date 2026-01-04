"""Admin-related keyboards."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ecombot.schemas.dto import OrderDTO
from ecombot.schemas.enums import OrderStatus

from ..callback_data import (
    AdminCallbackFactory,
    AdminNavCallbackFactory,
    EditProductCallbackFactory,
    OrderCallbackFactory,
)


def get_admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Builds the main keyboard for the admin panel."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="➕ Add Category",
        callback_data=AdminCallbackFactory(action="add_category"),
    )
    builder.button(
        text="❌ Delete Category",
        callback_data=AdminCallbackFactory(action="delete_category"),
    )
    builder.button(
        text="➕ Add Product",
        callback_data=AdminCallbackFactory(action="add_product"),
    )
    builder.button(
        text="📝 Edit Product",
        callback_data=AdminCallbackFactory(action="edit_product"),
    )
    builder.button(
        text="❌ Delete Product",
        callback_data=AdminCallbackFactory(action="delete_product"),
    )
    builder.button(
        text="📦 View Orders",
        callback_data=AdminCallbackFactory(action="view_orders"),
    )
    builder.adjust(2, 3, 1)
    return builder.as_markup()


def get_admin_orders_list_keyboard(orders: list[OrderDTO]) -> InlineKeyboardMarkup:
    """Builds a keyboard for the admin orders list with back to filters button."""
    builder = InlineKeyboardBuilder()
    for order in orders:
        builder.button(
            text=f"{order.order_number} - {order.contact_name}"
            f" (${order.total_price:.2f})",
            callback_data=OrderCallbackFactory(action="view_details", item_id=order.id),
        )

    builder.button(
        text="⬅️ Back to Filters",
        callback_data=AdminCallbackFactory(action="view_orders"),
    )
    builder.adjust(1)
    return builder.as_markup()


def get_admin_order_filters_keyboard() -> InlineKeyboardMarkup:
    """Builds a keyboard for filtering orders in the admin panel."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⏳ Pending",
        callback_data=f"admin_order_filter:{OrderStatus.PENDING.value}",
    )
    builder.button(
        text="⚙️ Processing",
        callback_data=f"admin_order_filter:{OrderStatus.PROCESSING.value}",
    )
    builder.button(
        text="🚚 Shipped",
        callback_data=f"admin_order_filter:{OrderStatus.SHIPPED.value}",
    )
    builder.button(
        text="✅ Completed",
        callback_data=f"admin_order_filter:{OrderStatus.COMPLETED.value}",
    )
    builder.button(
        text="❌ Cancelled",
        callback_data=f"admin_order_filter:{OrderStatus.CANCELLED.value}",
    )
    builder.button(
        text="⬅️ Back to Admin Panel",
        callback_data=AdminCallbackFactory(action="back_main"),
    )
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup()


def get_admin_order_details_keyboard(order: OrderDTO) -> InlineKeyboardMarkup:
    """Builds the action keyboard for an admin viewing an order's details."""
    builder = InlineKeyboardBuilder()

    # Logic to show the NEXT valid status, not all statuses
    if order.status == OrderStatus.PENDING:
        builder.button(
            text="Mark as Processing",
            callback_data=f"admin_order_status:{order.id}:{OrderStatus.PROCESSING.value}",
        )
    elif order.status == OrderStatus.PROCESSING:
        builder.button(
            text="Mark as Shipped",
            callback_data=f"admin_order_status:{order.id}:{OrderStatus.SHIPPED.value}",
        )
    elif order.status == OrderStatus.SHIPPED:
        builder.button(
            text="Mark as Completed",
            callback_data=f"admin_order_status:{order.id}:{OrderStatus.COMPLETED.value}",
        )

    if order.status not in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]:
        builder.button(
            text="Cancel Order",
            callback_data=f"admin_order_status:{order.id}:{OrderStatus.CANCELLED.value}",
        )

    builder.button(
        text="⬅️ Back to Orders List",
        callback_data=f"admin_order_filter:{order.status.value}",
    )
    builder.adjust(1)
    return builder.as_markup()


def get_edit_product_menu_keyboard(
    product_id: int,
    product_list_message_id: int,  # The ID of the message to go back to
    category_id: int,
) -> InlineKeyboardMarkup:
    """Builds a keyboard for choosing which product attribute to edit."""
    builder = InlineKeyboardBuilder()

    fields_to_edit = {
        "name": "📝 Name",
        "description": "📄 Description",
        "price": "💰 Price",
        "stock": "📦 Stock",
    }

    for field, text in fields_to_edit.items():
        builder.button(
            text=text,
            callback_data=EditProductCallbackFactory(
                action=field, product_id=product_id
            ),
        )

    builder.button(
        text="🖼️ Change Photo",
        callback_data=EditProductCallbackFactory(
            action="change_photo", product_id=product_id
        ),
    )

    builder.button(
        text="⬅️ Back to Products",
        callback_data=AdminNavCallbackFactory(
            action="back_to_product_list",
            target_message_id=product_list_message_id,
            category_id=category_id,
        ),
    )

    builder.adjust(2)
    return builder.as_markup()