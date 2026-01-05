"""Cart viewing handlers."""

from aiogram import F
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import CartCallbackFactory
from ecombot.bot.keyboards.cart import get_cart_keyboard
from ecombot.core import manager
from ecombot.logging_setup import log
from ecombot.services import cart_service
from ecombot.services.cart_service import InsufficientStockError
from ecombot.services.cart_service import ProductNotFoundError

from .utils import format_cart_text


router = Router()


@router.message(Command("cart"))
async def view_cart_handler(message: Message, session: AsyncSession):
    """Handle the /cart command to display the user's current cart."""
    if not message.from_user:
        error_msg = manager.get_message("cart", "error_user_not_identified")
        await message.answer(error_msg)
        return

    user_id = message.from_user.id
    cart_dto = await cart_service.get_user_cart(session, user_id)

    text = format_cart_text(cart_dto)
    keyboard = get_cart_keyboard(cart_dto)
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(CartCallbackFactory.filter(F.action == "add"))  # type: ignore[arg-type]
async def add_to_cart_handler(
    query: CallbackQuery, callback_data: CartCallbackFactory, session: AsyncSession
):
    """Handle the 'Add to Cart' button click from a product view."""
    if not query.from_user:
        error_msg = manager.get_message("cart", "error_user_not_identified")
        await query.answer(error_msg, show_alert=True)
        return

    user_id = query.from_user.id
    product_id = callback_data.item_id

    try:
        await cart_service.add_product_to_cart(
            session=session,
            user_id=user_id,
            product_id=product_id,
        )
        success_msg = manager.get_message("cart", "success_added_to_cart")
        await query.answer(success_msg, show_alert=False)

    except (InsufficientStockError, ProductNotFoundError) as e:
        await query.answer(str(e), show_alert=True)
    except Exception as e:
        log.error("Error adding to cart: {}", e)
        error_msg = manager.get_message("cart", "error_add_to_cart_failed")
        await query.answer(error_msg, show_alert=True)
