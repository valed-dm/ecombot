"""Utilities for order handlers."""

import contextlib
from html import escape

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.keyboards.orders import get_orders_list_keyboard
from ecombot.core.manager import central_manager as manager
from ecombot.db.models import User
from ecombot.schemas.dto import OrderDTO
from ecombot.services import order_service


def format_order_list_text(user_orders: list[OrderDTO]) -> str:
    """Format the order history list text."""
    header = manager.get_message("orders", "order_history_header")
    text_parts = [header]

    if not user_orders:
        no_orders_msg = manager.get_message("orders", "no_orders_message")
        text_parts.append(no_orders_msg)
        return "".join(text_parts)

    date_format = manager.get_message("orders", "date_format")
    for order in user_orders:
        order_item = manager.get_message(
            "orders",
            "order_list_item",
            order_number=escape(order.order_number),
            status=order.status.capitalize(),
            date=order.created_at.strftime(date_format),
            total=order.total_price,
        )
        text_parts.append(order_item)

    return "".join(text_parts)


def format_order_details_text(order_details: OrderDTO) -> str:
    """Format the order details text."""
    header = manager.get_message(
        "orders", "order_details_header", order_id=order_details.id
    )
    items_header = manager.get_message("orders", "order_items_header")

    text_parts = [
        header,
        f"Status: <i>{order_details.status.capitalize()}</i>\n\n",
        items_header,
    ]

    has_deleted_products = False
    active_total = 0.0
    deleted_total = 0.0

    for item in order_details.items:
        item_total = float(item.price * item.quantity)

        # Check if product is soft-deleted
        is_deleted = item.product.deleted_at is not None

        if is_deleted:
            product_status = " ⚠️ <i>(Deleted)</i>"
            has_deleted_products = True
            deleted_total += item_total
        else:
            product_status = ""
            active_total += item_total

        item_text = manager.get_message(
            "orders",
            "order_item_template",
            name=escape(item.product.name) + product_status,
            quantity=item.quantity,
            price=item.price,
            total=item_total,
        )
        text_parts.append(item_text)

    # Show totals breakdown
    text_parts.append("\n")
    if has_deleted_products:
        text_parts.extend(
            [
                f"<b>Active Items: ${active_total:.2f}</b>\n",
                f"<s>Deleted Items: ${deleted_total:.2f}</s>\n",
                f"<b>Total Paid: ${active_total:.2f}</b>",
            ]
        )
    else:
        text_parts.append(f"<b>Total: ${active_total:.2f}</b>")

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
