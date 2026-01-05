"""Utilities for admin order management."""

from html import escape

from aiogram.types import Message

from ecombot.bot.keyboards.admin import get_admin_order_details_keyboard
from ecombot.core.manager import central_manager as manager
from ecombot.logging_setup import log
from ecombot.schemas.dto import OrderDTO


class InvalidQueryDataError(ValueError):
    """Raised when query data is invalid or missing."""

    pass


def generate_order_details_text(order: OrderDTO) -> str:
    """Generate detailed text for a single order."""
    not_available = manager.get_message("admin_orders", "not_available")

    text_parts = [
        manager.get_message(
            "admin_orders",
            "order_details_header",
            order_number=escape(order.order_number),
        ),
        manager.get_message(
            "admin_orders", "order_status_field", status=order.status.capitalize()
        ),
        manager.get_message(
            "admin_orders",
            "order_date_field",
            date=order.created_at.strftime("%Y-%m-%d %H:%M"),
        ),
        manager.get_message(
            "admin_orders",
            "customer_info_header",
            name=escape(order.contact_name or not_available),
            phone=escape(order.phone or not_available),
            address=escape(order.address or not_available),
        ),
        manager.get_message("admin_orders", "items_header"),
    ]

    has_deleted_products = False
    active_total = 0.0
    deleted_total = 0.0

    for item in order.items:
        item_total = float(item.price * item.quantity)

        # Check if product is soft-deleted
        is_deleted = item.product.deleted_at is not None

        if is_deleted:
            product_status = manager.get_message(
                "admin_orders", "deleted_product_suffix"
            )
            has_deleted_products = True
            deleted_total += item_total
        else:
            product_status = ""
            active_total += item_total

        text_parts.append(
            manager.get_message(
                "admin_orders",
                "item_template",
                name=escape(item.product.name),
                status=product_status,
                quantity=item.quantity,
                price=item.price,
                total=item_total,
            )
        )

    # Show totals breakdown
    text_parts.append("\n")
    if has_deleted_products:
        text_parts.extend(
            [
                manager.get_message(
                    "admin_orders", "active_items_total", total=active_total
                ),
                manager.get_message(
                    "admin_orders", "deleted_items_total", total=deleted_total
                ),
                manager.get_message("admin_orders", "final_total", total=active_total),
                manager.get_message("admin_orders", "deleted_items_notice"),
            ]
        )
    else:
        text_parts.append(
            manager.get_message("admin_orders", "order_total", total=active_total)
        )

    text = "".join(text_parts)

    # Check Telegram's character limit
    max_length = int(manager.get_message("admin_orders", "max_message_length"))
    truncate_threshold = int(manager.get_message("admin_orders", "truncate_threshold"))

    if len(text) > max_length:
        text = text[:truncate_threshold] + manager.get_message(
            "admin_orders", "text_truncated_suffix"
        )

    return text


async def send_order_details_view(message: Message, order: OrderDTO):
    """Generate and send the detailed view for a single order for an admin."""
    text = generate_order_details_text(order)
    keyboard = get_admin_order_details_keyboard(order)

    try:
        await message.edit_text(text, reply_markup=keyboard)
    except Exception as e:
        log.error(f"Failed to edit order details message: {e}", exc_info=True)
        # Fallback: send as new message if edit fails
        await message.answer(text, reply_markup=keyboard)
