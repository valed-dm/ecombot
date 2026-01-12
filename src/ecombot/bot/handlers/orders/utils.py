"""Utilities for order handlers."""

import contextlib
from html import escape

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import OrderCallbackFactory
from ecombot.config import settings
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

    return "".join(text_parts)


def format_order_details_text(order_details: OrderDTO) -> str:
    """Format the order details text."""
    header = manager.get_message(
        "orders", "order_details_header", order_id=order_details.display_order_number
    )
    items_header = manager.get_message("orders", "order_items_header")

    status_text = manager.get_message("common", order_details.status.message_key)
    date_format = manager.get_message("orders", "date_format")

    # Convert UTC timestamp to configured timezone for display
    local_date = order_details.created_at.astimezone(settings.get_zoneinfo())

    text_parts = [
        header,
        manager.get_message(
            "orders",
            "order_date_line",
            date=local_date.strftime(date_format),
        ),
        manager.get_message(
            "orders",
            "order_address_line",
            address=escape(order_details.shipping_address),
        ),
        manager.get_message("orders", "status_line", status=status_text),
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
            product_status = manager.get_message("orders", "deleted_product_suffix")
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
                manager.get_message("orders", "active_items_total", total=active_total),
                manager.get_message(
                    "orders", "deleted_items_total", total=deleted_total
                ),
                manager.get_message("orders", "total_paid", total=active_total),
            ]
        )
    else:
        text_parts.append(
            manager.get_message("orders", "total_label", total=active_total)
        )

    return "".join(text_parts)


async def send_orders_view(
    message: Message, session: AsyncSession, db_user: User, page: int = 1
):
    """Generate and send the main order history view."""
    items_per_page = 5
    user_orders = await order_service.list_user_orders(session, db_user.id)
    text = format_order_list_text(user_orders)

    if not user_orders:
        await message.answer(text)
        return

    # Pagination logic
    total_pages = (len(user_orders) + items_per_page - 1) // items_per_page
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    current_page_orders = user_orders[start_idx:end_idx]

    builder = InlineKeyboardBuilder()
    for order in current_page_orders:
        status_text = manager.get_message("common", order.status.message_key)
        status_text = f"{status_text: <12}"
        button_text = manager.get_message(
            "orders",
            "order_list_button",
            order_id=order.display_order_number,
            status=status_text,
            total=order.total_price,
        )
        builder.button(
            text=button_text,
            callback_data=OrderCallbackFactory(action="view_details", item_id=order.id),
        )

    # Navigation buttons
    nav_buttons = []
    if page > 1:
        nav_buttons.append(
            builder.button(
                text="⬅️",
                callback_data=OrderCallbackFactory(action="list", item_id=page - 1),
            )
        )
    if page < total_pages:
        nav_buttons.append(
            builder.button(
                text="➡️",
                callback_data=OrderCallbackFactory(action="list", item_id=page + 1),
            )
        )
    builder.adjust(1)
    keyboard = builder.as_markup()

    try:
        await message.edit_text(text, reply_markup=keyboard)
    except TelegramBadRequest:
        with contextlib.suppress(TelegramBadRequest):
            await message.delete()
        await message.answer(text, reply_markup=keyboard)
