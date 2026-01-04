"""Utilities for cart handlers."""

from typing import Literal

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import CartCallbackFactory
from ecombot.bot.keyboards.cart import get_cart_keyboard
from ecombot.logging_setup import log
from ecombot.schemas.dto import CartDTO
from ecombot.services import cart_service
from ecombot.services.cart_service import CartItemNotFoundError

from .constants import CART_EMPTY_MESSAGE
from .constants import CART_HEADER
from .constants import CART_PADDING
from .constants import CART_SEPARATOR
from .constants import ERROR_CART_ITEM_NOT_FOUND
from .constants import ERROR_CART_UPDATE_FAILED
from .constants import ERROR_GENERIC
from .constants import ERROR_USER_NOT_IDENTIFIED
from .constants import SUCCESS_ITEM_REMOVED
from .constants import SUCCESS_QUANTITY_DECREASED
from .constants import SUCCESS_QUANTITY_INCREASED


def format_cart_text(cart_dto: CartDTO) -> str:
    """Format the cart's contents into a clean, monospaced, wide block of text."""
    if not cart_dto.items:
        return CART_EMPTY_MESSAGE

    header = CART_HEADER
    lines = [""]  # Start with empty line after header

    item_lines = []
    for item in cart_dto.items:
        item_total = item.product.price * item.quantity
        line = (
            f"▪️ {item.product.name}\n  {item.quantity} x ${item.product.price:,.2f}"
            f" = ${item_total:,.2f}"
        )
        item_lines.append(line)

    lines.extend(item_lines)
    lines.append(CART_SEPARATOR)
    total_line = f"Total: ${cart_dto.total_price:,.2f}"
    lines.append(total_line)

    # Find the length of the longest line and add padding
    max_len = max(len(line) for line in lines) + CART_PADDING
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
        await query.answer(ERROR_USER_NOT_IDENTIFIED, show_alert=True)
        return

    user_id = query.from_user.id
    cart_item_id = callback_data.item_id

    try:
        updated_cart = await cart_service.alter_item_quantity(
            session, user_id, cart_item_id, action
        )
        success = await update_cart_view(callback_message, updated_cart)
        if not success:
            await query.answer(ERROR_CART_UPDATE_FAILED, show_alert=True)
            return

        feedback_text = {
            "increase": SUCCESS_QUANTITY_INCREASED,
            "decrease": SUCCESS_QUANTITY_DECREASED,
            "remove": SUCCESS_ITEM_REMOVED,
        }
        await query.answer(feedback_text.get(action))

    except CartItemNotFoundError:
        await query.answer(ERROR_CART_ITEM_NOT_FOUND, show_alert=True)
        fresh_cart = await cart_service.get_user_cart(session, user_id)
        await update_cart_view(callback_message, fresh_cart)
    except Exception as e:
        log.error(f"Error altering cart item: {e}", exc_info=True)
        await query.answer(ERROR_GENERIC, show_alert=True)
