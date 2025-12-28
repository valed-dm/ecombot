"""
Handlers for the shopping cart.

This module contains handlers for adding items to the cart, viewing the cart,
and initiating the checkout process.
"""

from typing import Literal

from aiogram import F
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot import keyboards
from ecombot.bot.callback_data import CartCallbackFactory
from ecombot.bot.middlewares import MessageInteractionMiddleware
from ecombot.logging_setup import log
from ecombot.schemas.dto import CartDTO
from ecombot.services import cart_service
from ecombot.services.cart_service import CartItemNotFoundError
from ecombot.services.cart_service import InsufficientStockError
from ecombot.services.cart_service import ProductNotFoundError


# =============================================================================
# Router and Middleware Setup
# =============================================================================

router = Router()
router.callback_query.middleware(MessageInteractionMiddleware())

# =============================================================================
# Helper Functions
# =============================================================================


def format_cart_text(cart_dto: CartDTO) -> str:
    """
    Formats the cart's contents into a clean, monospaced, wide block of text.
    """
    if not cart_dto.items:
        return "🛒 <b>Your Shopping Cart</b>\n\nYour cart is currently empty."

    header = "🛒 Your Shopping Cart"
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
    lines.append("-" * 50)
    total_line = f"Total: ${cart_dto.total_price:,.2f}"
    lines.append(total_line)

    # Find the length of the longest line and add padding
    max_len = max(len(line) for line in lines) + 4
    padded_lines = [line.ljust(max_len) for line in lines]

    final_text = "\n".join(padded_lines)
    return f"<b>{header}</b>\n<pre>{final_text}</pre>"


async def update_cart_view(message: Message, cart_dto: CartDTO) -> bool:
    """
    Helper function to edit a message to show the updated cart view.
    Returns True on success, False on failure.
    """
    text = format_cart_text(cart_dto)
    keyboard = keyboards.get_cart_keyboard(cart_dto)

    try:
        await message.edit_text(text, reply_markup=keyboard)
        return True
    except TelegramBadRequest as e:
        if "message is not modified" not in e.message:
            log.error(f"Error updating cart view: {e}")
            return False
        return True  # Not modified is considered success


# =============================================================================
# Main Cart Handlers
# =============================================================================


@router.message(Command("cart"))
async def view_cart_handler(message: Message, session: AsyncSession):
    """
    Handles the /cart command to display the user's current cart.
    """
    if not message.from_user:
        await message.answer("Could not identify you.")
        return

    user_id = message.from_user.id
    cart_dto = await cart_service.get_user_cart(session, user_id)

    text = format_cart_text(cart_dto)
    keyboard = keyboards.get_cart_keyboard(cart_dto)
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(CartCallbackFactory.filter(F.action == "add"))  # type: ignore[arg-type]
async def add_to_cart_handler(
    query: CallbackQuery, callback_data: CartCallbackFactory, session: AsyncSession
):
    """
    Handles the 'Add to Cart' button click from a product view.
    """
    if not query.from_user:
        await query.answer("Could not identify user.", show_alert=True)
        return

    user_id = query.from_user.id
    product_id = callback_data.item_id

    try:
        await cart_service.add_product_to_cart(
            session=session,
            user_id=user_id,
            product_id=product_id,
        )
        await query.answer("✅ Product added to your cart!", show_alert=False)

    except (InsufficientStockError, ProductNotFoundError) as e:
        await query.answer(str(e), show_alert=True)
    except Exception as e:
        log.error("Error adding to cart: {}", e)
        await query.answer("An error occurred while adding to cart.", show_alert=True)


# =============================================================================
# Cart Item Quantity Alteration Handlers
# =============================================================================


async def alter_cart_item(
    query: CallbackQuery,
    callback_data: CartCallbackFactory,
    session: AsyncSession,
    callback_message: Message,
    action: Literal["increase", "decrease", "remove"],
):
    """Generic helper to call the service and update the cart view."""
    if not query.from_user:
        await query.answer("Could not identify user.", show_alert=True)
        return

    user_id = query.from_user.id
    cart_item_id = callback_data.item_id

    try:
        updated_cart = await cart_service.alter_item_quantity(
            session, user_id, cart_item_id, action
        )
        success = await update_cart_view(callback_message, updated_cart)
        if not success:
            await query.answer("Failed to update cart display.", show_alert=True)
            return

        feedback_text = {
            "increase": "Quantity +1",
            "decrease": "Quantity -1",
            "remove": "Item removed",
        }
        await query.answer(feedback_text.get(action))

    except CartItemNotFoundError:
        await query.answer("This item is no longer in your cart.", show_alert=True)
        fresh_cart = await cart_service.get_user_cart(session, user_id)
        await update_cart_view(callback_message, fresh_cart)
    except Exception as e:
        log.error(f"Error altering cart item: {e}", exc_info=True)
        await query.answer("An error occurred.", show_alert=True)


@router.callback_query(CartCallbackFactory.filter(F.action == "decrease"))  # type: ignore[arg-type]
async def decrease_cart_item_handler(
    query: CallbackQuery,
    callback_data: CartCallbackFactory,
    session: AsyncSession,
    callback_message: Message,
):
    await alter_cart_item(
        query, callback_data, session, callback_message, action="decrease"
    )


@router.callback_query(CartCallbackFactory.filter(F.action == "increase"))  # type: ignore[arg-type]
async def increase_cart_item_handler(
    query: CallbackQuery,
    callback_data: CartCallbackFactory,
    session: AsyncSession,
    callback_message: Message,
):
    await alter_cart_item(
        query, callback_data, session, callback_message, action="increase"
    )


@router.callback_query(CartCallbackFactory.filter(F.action == "remove"))  # type: ignore[arg-type]
async def remove_cart_item_handler(
    query: CallbackQuery,
    callback_data: CartCallbackFactory,
    session: AsyncSession,
    callback_message: Message,
):
    await alter_cart_item(
        query, callback_data, session, callback_message, action="remove"
    )
