"""Admin-related keyboards."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ecombot.core.manager import central_manager as manager
from ecombot.schemas.dto import OrderDTO
from ecombot.schemas.enums import OrderStatus

from ..callback_data import AddProductImageCallbackFactory
from ..callback_data import AdminCallbackFactory
from ..callback_data import AdminNavCallbackFactory
from ..callback_data import DeliveryAdminCallbackFactory
from ..callback_data import EditProductCallbackFactory
from ..callback_data import OrderCallbackFactory


def get_admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Builds the main keyboard for the admin panel."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text=manager.get_message("keyboards", "add_category"),
        callback_data=AdminCallbackFactory(action="add_category"),
    )
    builder.button(
        text=manager.get_message("keyboards", "delete_category"),
        callback_data=AdminCallbackFactory(action="delete_category"),
    )
    builder.button(
        text=manager.get_message("keyboards", "restore_category"),
        callback_data=AdminCallbackFactory(action="restore_category"),
    )
    builder.button(
        text=manager.get_message("keyboards", "add_product"),
        callback_data=AdminCallbackFactory(action="add_product"),
    )
    builder.button(
        text=manager.get_message("keyboards", "edit_product"),
        callback_data=AdminCallbackFactory(action="edit_product"),
    )
    builder.button(
        text=manager.get_message("keyboards", "delete_product"),
        callback_data=AdminCallbackFactory(action="delete_product"),
    )
    builder.button(
        text=manager.get_message("keyboards", "restore_product"),
        callback_data=AdminCallbackFactory(action="restore_product"),
    )
    builder.button(
        text=manager.get_message("keyboards", "view_orders"),
        callback_data=AdminCallbackFactory(action="view_orders"),
    )
    builder.button(
        text=manager.get_message("keyboards", "manage_delivery"),
        callback_data=DeliveryAdminCallbackFactory(action="menu"),
    )
    builder.adjust(3, 4, 2)
    return builder.as_markup()


def get_admin_orders_list_keyboard(orders: list[OrderDTO]) -> InlineKeyboardMarkup:
    """Builds a keyboard for the admin orders list with back to filters button."""
    builder = InlineKeyboardBuilder()
    currency = manager.get_message("common", "currency_symbol")
    for order in orders:
        builder.button(
            text=f"{order.order_number} - {order.contact_name}"
            f" ({currency}{order.total_price:.2f})",
            callback_data=OrderCallbackFactory(action="view_details", item_id=order.id),
        )

    builder.button(
        text=manager.get_message("keyboards", "back_to_filters"),
        callback_data=AdminCallbackFactory(action="view_orders"),
    )
    builder.adjust(1)
    return builder.as_markup()


def get_admin_order_filters_keyboard() -> InlineKeyboardMarkup:
    """Builds a keyboard for filtering orders in the admin panel."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text=manager.get_message("keyboards", "pending"),
        callback_data=f"admin_order_filter:{OrderStatus.PENDING.value}",
    )
    builder.button(
        text=manager.get_message("keyboards", "processing"),
        callback_data=f"admin_order_filter:{OrderStatus.PROCESSING.value}",
    )
    builder.button(
        text=manager.get_message("keyboards", "pickup_ready"),
        callback_data=f"admin_order_filter:{OrderStatus.PICKUP_READY.value}",
    )
    builder.button(
        text=manager.get_message("keyboards", "shipped"),
        callback_data=f"admin_order_filter:{OrderStatus.SHIPPED.value}",
    )
    builder.button(
        text=manager.get_message("keyboards", "mark_as_paid"),
        callback_data=f"admin_order_filter:{OrderStatus.PAID.value}",
    )
    builder.button(
        text=manager.get_message("keyboards", "completed"),
        callback_data=f"admin_order_filter:{OrderStatus.COMPLETED.value}",
    )
    builder.button(
        text=manager.get_message("keyboards", "cancelled"),
        callback_data=f"admin_order_filter:{OrderStatus.CANCELLED.value}",
    )
    builder.button(
        text=manager.get_message("keyboards", "refunded"),
        callback_data=f"admin_order_filter:{OrderStatus.REFUNDED.value}",
    )
    builder.button(
        text=manager.get_message("keyboards", "failed"),
        callback_data=f"admin_order_filter:{OrderStatus.FAILED.value}",
    )
    builder.button(
        text=manager.get_message("keyboards", "back_to_admin_panel"),
        callback_data=AdminCallbackFactory(action="back_main"),
    )
    builder.adjust(2, 2, 2)
    return builder.as_markup()


def get_admin_order_details_keyboard(order: OrderDTO) -> InlineKeyboardMarkup:
    """Builds the action keyboard for an admin viewing an order's details."""
    builder = InlineKeyboardBuilder()

    # Logic to show the NEXT valid status, not all statuses
    if order.status == OrderStatus.PENDING:
        builder.button(
            text=manager.get_message("keyboards", "mark_as_processing"),
            callback_data=f"admin_order_status:{order.id}:{OrderStatus.PROCESSING.value}",
        )
    elif order.status == OrderStatus.PROCESSING:
        builder.button(
            text=manager.get_message("keyboards", "mark_as_pickup_ready"),
            callback_data=f"admin_order_status:{order.id}:{OrderStatus.PICKUP_READY.value}",
        )
        builder.button(
            text=manager.get_message("keyboards", "mark_as_shipped"),
            callback_data=f"admin_order_status:{order.id}:{OrderStatus.SHIPPED.value}",
        )
    elif order.status in [OrderStatus.SHIPPED, OrderStatus.PICKUP_READY]:
        builder.button(
            text=manager.get_message("keyboards", "mark_as_paid"),
            callback_data=f"admin_order_status:{order.id}:{OrderStatus.PAID.value}",
        )
    if order.status == OrderStatus.PICKUP_READY:
        builder.button(
            text=manager.get_message("keyboards", "mark_as_shipped"),
            callback_data=f"admin_order_status:{order.id}:{OrderStatus.SHIPPED.value}",
        )
    elif order.status in [
        OrderStatus.PAID,
        OrderStatus.PICKUP_READY,
        OrderStatus.SHIPPED,
    ]:
        builder.button(
            text=manager.get_message("keyboards", "mark_as_completed"),
            callback_data=f"admin_order_status:{order.id}:{OrderStatus.COMPLETED.value}",
        )

    if order.status not in [
        OrderStatus.COMPLETED,
        OrderStatus.CANCELLED,
        OrderStatus.REFUNDED,
        OrderStatus.FAILED,
    ]:
        builder.button(
            text=manager.get_message("keyboards", "cancel_order"),
            callback_data=f"admin_order_status:{order.id}:{OrderStatus.CANCELLED.value}",
        )

    builder.button(
        text=manager.get_message("keyboards", "back_to_orders_list"),
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
        "name": manager.get_message("keyboards", "edit_name"),
        "description": manager.get_message("keyboards", "edit_description"),
        "price": manager.get_message("keyboards", "edit_price"),
        "stock": manager.get_message("keyboards", "edit_stock"),
    }

    for field, text in fields_to_edit.items():
        builder.button(
            text=text,
            callback_data=EditProductCallbackFactory(
                action=field, product_id=product_id
            ),
        )

    builder.button(
        text=manager.get_message("keyboards", "change_photo"),
        callback_data=EditProductCallbackFactory(
            action="change_photo", product_id=product_id
        ),
    )

    builder.button(
        text=manager.get_message("keyboards", "back_to_products"),
        callback_data=AdminNavCallbackFactory(
            action="back_to_product_list",
            target_message_id=product_list_message_id,
            category_id=category_id,
        ),
    )

    builder.adjust(2)
    return builder.as_markup()


def get_add_product_image_keyboard() -> InlineKeyboardMarkup:
    """Builds a keyboard for the image upload step (Done/Skip)."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text=manager.get_message("keyboards", "done"),
        callback_data=AddProductImageCallbackFactory(action="done"),
    )
    builder.button(
        text=manager.get_message("keyboards", "skip"),
        callback_data=AddProductImageCallbackFactory(action="skip"),
    )
    builder.adjust(2)
    return builder.as_markup()
