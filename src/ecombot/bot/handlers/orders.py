"""
Handlers for viewing user order history.
"""

import contextlib
from html import escape

from aiogram import F
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot import keyboards
from ecombot.bot.callback_data import OrderCallbackFactory
from ecombot.bot.middlewares import MessageInteractionMiddleware
from ecombot.db.models import User
from ecombot.services import order_service


# =============================================================================
# Router and Middleware Setup
# =============================================================================


router = Router()
router.callback_query.middleware(MessageInteractionMiddleware())


# =============================================================================
# Helper Function
# =============================================================================


async def send_orders_view(message: Message, session: AsyncSession, db_user: User):
    """
    A helper function to generate and send the main order history view.
    """
    user_orders = await order_service.list_user_orders(session, db_user.id)
    text_parts = ["<b>Your Order History</b>\n\n"]

    if not user_orders:
        text_parts.append("You have not placed any orders yet.")
        await message.answer("".join(text_parts))
        return

    for order in user_orders:
        text_parts.append(
            f"📦 <b>Order #{escape(order.order_number)}</b>"
            f" - <i>{order.status.capitalize()}</i>\n"
            f"Placed on: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"Total: ${order.total_price:.2f}\n\n"
        )

    text = "".join(text_parts)

    keyboard = keyboards.get_orders_list_keyboard(user_orders)

    try:
        await message.edit_text(text, reply_markup=keyboard)
    except TelegramBadRequest:
        with contextlib.suppress(TelegramBadRequest):
            await message.delete()
        await message.answer(text, reply_markup=keyboard)


# =============================================================================
# Main Handlers
# =============================================================================


@router.message(Command("orders"))
async def view_orders_handler(message: Message, session: AsyncSession, db_user: User):
    """Handles the /orders command to display the user's order history."""
    await send_orders_view(message, session, db_user)


@router.callback_query(OrderCallbackFactory.filter(F.action == "view_details"))  # type: ignore[arg-type]
async def view_order_details_handler(
    query: CallbackQuery,
    callback_data: OrderCallbackFactory,
    session: AsyncSession,
    db_user: User,
    callback_message: Message,
):
    """Handles the 'View Details' button click for a specific order."""
    order_details = None
    order_id = callback_data.item_id
    if order_id:
        order_details = await order_service.get_order_details(
            session,
            order_id,
            db_user.id,
        )

    if not order_details:
        await query.answer("Could not find this order.", show_alert=True)
        return

    text_parts = [
        f"<b>Details for Order #{order_details.id}</b>\n"
        f"Status: <i>{order_details.status.capitalize()}</i>\n\n"
        "<b>Items:</b>\n"
    ]

    for item in order_details.items:
        item_total = item.price * item.quantity
        text_parts.append(
            f"  - <b>{escape(item.product.name)}</b>\n"
            f"    <code>{item.quantity} x ${item.price:.2f}"
            f" = ${item_total:.2f}</code>\n"
        )

    text_parts.append(f"\n<b>Total: ${order_details.total_price:.2f}</b>")
    text = "".join(text_parts)

    keyboard = keyboards.get_order_details_keyboard()
    await callback_message.edit_text(text, reply_markup=keyboard)
    await query.answer()


@router.callback_query(OrderCallbackFactory.filter(F.action == "back_to_list"))  # type: ignore[arg-type]
async def back_to_orders_handler(
    query: CallbackQuery,
    session: AsyncSession,
    db_user: User,
    callback_message: Message,
):
    """Handles the 'Back to Order History' button click."""
    await send_orders_view(callback_message, session, db_user)
    await query.answer()
