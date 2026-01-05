"""Order details handlers."""

from aiogram import F
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import OrderCallbackFactory
from ecombot.bot.keyboards.orders import get_order_details_keyboard
from ecombot.core import manager
from ecombot.db.models import User
from ecombot.services import order_service

from .utils import format_order_details_text


router = Router()


@router.callback_query(OrderCallbackFactory.filter(F.action == "view_details"))  # type: ignore[arg-type]
async def view_order_details_handler(
    query: CallbackQuery,
    callback_data: OrderCallbackFactory,
    session: AsyncSession,
    db_user: User,
    callback_message: Message,
):
    """Handle the 'View Details' button click for a specific order."""
    order_details = None
    order_id = callback_data.item_id
    if order_id:
        order_details = await order_service.get_order_details(
            session,
            order_id,
            db_user.id,
        )

    if not order_details:
        error_msg = manager.get_message("orders", "error_order_not_found")
        await query.answer(error_msg, show_alert=True)
        return

    text = format_order_details_text(order_details)
    keyboard = get_order_details_keyboard()
    await callback_message.edit_text(text, reply_markup=keyboard)
    await query.answer()
