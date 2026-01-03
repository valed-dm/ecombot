"""Utilities for admin order management."""

from html import escape

from aiogram.types import Message

from ecombot.bot import keyboards
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

    for item in order.items:
        item_total = item.price * item.quantity
        text_parts.extend(
            [
                f"  - <b>{escape(item.product.name)}</b>\n",
                f"    <code>{item.quantity} x ${item.price:.2f}",
                f" = ${item_total:.2f}</code>\n",
            ]
        )

    text_parts.append(f"\n<b>Total: ${order.total_price:.2f}</b>")
    text = "".join(text_parts)

    # Check Telegram's character limit
    if len(text) > MAX_MESSAGE_LENGTH:
        text = text[:TRUNCATE_THRESHOLD] + TEXT_TRUNCATED_SUFFIX

    return text


async def send_order_details_view(message: Message, order: OrderDTO):
    """Generate and send the detailed view for a single order for an admin."""
    text = generate_order_details_text(order)
    keyboard = keyboards.get_admin_order_details_keyboard(order)

    try:
        await message.edit_text(text, reply_markup=keyboard)
    except Exception as e:
        log.error(f"Failed to edit order details message: {e}", exc_info=True)
        # Fallback: send as new message if edit fails
        await message.answer(text, reply_markup=keyboard)
