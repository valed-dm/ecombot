"""Utilities for admin order management."""

from html import escape

from aiogram.types import Message

from ecombot.bot.keyboards.admin import get_admin_order_details_keyboard
from ecombot.logging_setup import log
from ecombot.schemas.dto import OrderDTO

from .constants import MAX_MESSAGE_LENGTH
from .constants import TEXT_TRUNCATED_SUFFIX
from .constants import TRUNCATE_THRESHOLD


class InvalidQueryDataError(ValueError):
    """Raised when query data is invalid or missing."""

    pass


def generate_order_details_text(order: OrderDTO) -> str:
    """Generate detailed text for a single order."""
    text_parts = [
        f"<b>Order Details: {escape(order.order_number)}</b>\n\n",
        f"<b>Status:</b> <i>{order.status.capitalize()}</i>\n",
        f"<b>Placed on:</b> {order.created_at.strftime('%Y-%m-%d %H:%M')}\n\n",
        f"<b>Customer:</b> {escape(order.contact_name or 'N/A')}\n",
        f"<b>Phone:</b> <code>{escape(order.phone or 'N/A')}</code>\n",
        f"<b>Address:</b> <code>{escape(order.address or 'N/A')}</code>\n\n",
        "<b>Items:</b>\n",
    ]

    has_deleted_products = False
    active_total = 0.0
    deleted_total = 0.0

    for item in order.items:
        item_total = float(item.price * item.quantity)

        # Check if product is soft-deleted
        is_deleted = item.product.deleted_at is not None

        if is_deleted:
            product_status = " ⚠️ <i>(Deleted - Not Charged)</i>"
            has_deleted_products = True
            deleted_total += item_total
        else:
            product_status = ""
            active_total += item_total

        text_parts.extend(
            [
                f"  - <b>{escape(item.product.name)}</b>{product_status}\n",
                f"    <code>{item.quantity} x ${item.price:.2f}",
                f" = ${item_total:.2f}</code>\n",
            ]
        )

    # Show totals breakdown
    text_parts.append("\n")
    if has_deleted_products:
        text_parts.extend(
            [
                f"<b>Active Items Total: ${active_total:.2f}</b>\n",
                f"<s>Deleted Items: ${deleted_total:.2f}</s>\n",
                f"<b>Final Total: ${active_total:.2f}</b>\n\n",
                "⚠️ <i>Deleted products are not charged. "
                "Customer pays only for active items.</i>",
            ]
        )
    else:
        text_parts.append(f"<b>Total: ${active_total:.2f}</b>")

    text = "".join(text_parts)

    # Check Telegram's character limit
    if len(text) > MAX_MESSAGE_LENGTH:
        text = text[:TRUNCATE_THRESHOLD] + TEXT_TRUNCATED_SUFFIX

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
