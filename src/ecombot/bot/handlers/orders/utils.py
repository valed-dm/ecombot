"""Utilities for order handlers."""

import contextlib
from html import escape

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.keyboards.orders import get_orders_list_keyboard
from ecombot.db.models import User
from ecombot.schemas.dto import OrderDTO
from ecombot.services import order_service

from .constants import DATE_FORMAT
from .constants import NO_ORDERS_MESSAGE
from .constants import ORDER_DETAILS_HEADER
from .constants import ORDER_HISTORY_HEADER
from .constants import ORDER_ITEMS_HEADER


def format_order_list_text(user_orders: list[OrderDTO]) -> str:
    """Format the order history list text."""
    text_parts = [ORDER_HISTORY_HEADER]

    if not user_orders:
        text_parts.append(NO_ORDERS_MESSAGE)
        return "".join(text_parts)

    for order in user_orders:
        text_parts.append(
            f"📦 <b>Order #{escape(order.order_number)}</b>"
            f" - <i>{order.status.capitalize()}</i>\n"
            f"Placed on: {order.created_at.strftime(DATE_FORMAT)}\n"
            f"Total: ${order.total_price:.2f}\n\n"
        )

    return "".join(text_parts)


def format_order_details_text(order_details: OrderDTO) -> str:
    """Format the order details text."""
    text_parts = [
        ORDER_DETAILS_HEADER.format(order_id=order_details.id),
        f"Status: <i>{order_details.status.capitalize()}</i>\n\n",
        ORDER_ITEMS_HEADER,
    ]

    for item in order_details.items:
        item_total = item.price * item.quantity
        text_parts.append(
            f"  - <b>{escape(item.product.name)}</b>\n"
            f"    <code>{item.quantity} x ${item.price:.2f}"
            f" = ${item_total:.2f}</code>\n"
        )

    text_parts.append(f"\n<b>Total: ${order_details.total_price:.2f}</b>")
    return "".join(text_parts)


async def send_orders_view(message: Message, session: AsyncSession, db_user: User):
    """Generate and send the main order history view."""
    user_orders = await order_service.list_user_orders(session, db_user.id)
    text = format_order_list_text(user_orders)

    if not user_orders:
        await message.answer(text)
        return

    keyboard = get_orders_list_keyboard(user_orders)

    try:
        await message.edit_text(text, reply_markup=keyboard)
    except TelegramBadRequest:
        with contextlib.suppress(TelegramBadRequest):
            await message.delete()
        await message.answer(text, reply_markup=keyboard)
