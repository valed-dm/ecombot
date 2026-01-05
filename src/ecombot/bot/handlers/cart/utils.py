"""Utilities for cart handlers."""

from typing import Literal

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import CartCallbackFactory
from ecombot.bot.keyboards.cart import get_cart_keyboard
from ecombot.core.manager import central_manager as manager
from ecombot.logging_setup import log
from ecombot.schemas.dto import CartDTO
from ecombot.services import cart_service
from ecombot.services.cart_service import CartItemNotFoundError


def format_cart_text(cart_dto: CartDTO) -> str:
    """Format the cart's contents into a clean, monospaced, wide block of text."""
    if not cart_dto.items:
        return manager.get_message("cart", "cart_empty_message")

    header = manager.get_message("cart", "cart_header")
    lines = [""]  # Start with empty line after header

    item_lines = []
    for item in cart_dto.items:
        item_total = item.product.price * item.quantity
        line = manager.get_message(
            "cart",
            "cart_item_template",
            name=item.product.name,
            price=item.product.price,
            quantity=item.quantity,
            subtotal=item_total,
        )
        item_lines.append(line)

    lines.extend(item_lines)
    lines.append("-" * 50)  # separator
    total_line = manager.get_message("cart", "cart_total", total=cart_dto.total_price)
    lines.append(total_line)

    # Find the length of the longest line and add padding
    max_len = max(len(line) for line in lines) + 4  # padding
    padded_lines = [line.ljust(max_len) for line in lines]

    final_text = "\n".join(padded_lines)
    return f"<b>{header}</b>\n<pre>{final_text}</pre>"


async def update_cart_view(message: Message, cart_dto: CartDTO) -> bool:
    """
    Helper function to edit a message to show the updated cart view.
    Returns True on success, False on failure.
    """
    text = format_cart_text(cart_dto)
    keyboard = get_cart_keyboard(cart_dto)

    try:
        await message.edit_text(text, reply_markup=keyboard)
        return True
    except TelegramBadRequest as e:
        if "message is not modified" not in e.message:
            log.error(f"Error updating cart view: {e}")
            return False
        return True  # Not modified is considered success


async def alter_cart_item(
    query: CallbackQuery,
    callback_data: CartCallbackFactory,
    session: AsyncSession,
    callback_message: Message,
    action: Literal["increase", "decrease", "remove"],
):
    """Generic helper to call the service and update the cart view."""
    if not query.from_user:
        error_msg = manager.get_message("cart", "error_user_not_identified")
        await query.answer(error_msg, show_alert=True)
        return

    user_id = query.from_user.id
    cart_item_id = callback_data.item_id

    try:
        updated_cart = await cart_service.alter_item_quantity(
            session, user_id, cart_item_id, action
        )
        success = await update_cart_view(callback_message, updated_cart)
        if not success:
            error_msg = manager.get_message("cart", "error_cart_update_failed")
            await query.answer(error_msg, show_alert=True)
            return

        feedback_messages = {
            "increase": manager.get_message("cart", "success_quantity_increased"),
            "decrease": manager.get_message("cart", "success_quantity_decreased"),
            "remove": manager.get_message("cart", "success_item_removed"),
        }
        await query.answer(feedback_messages.get(action))

    except CartItemNotFoundError:
        error_msg = manager.get_message("cart", "error_cart_item_not_found")
        await query.answer(error_msg, show_alert=True)
        fresh_cart = await cart_service.get_user_cart(session, user_id)
        await update_cart_view(callback_message, fresh_cart)
    except Exception as e:
        log.error(f"Error altering cart item: {e}", exc_info=True)
        error_msg = manager.get_message("cart", "error_generic")
        await query.answer(error_msg, show_alert=True)
