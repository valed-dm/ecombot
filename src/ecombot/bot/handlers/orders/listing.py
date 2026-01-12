"""Order listing handlers."""

from aiogram import F
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import OrderCallbackFactory
from ecombot.db.models import User

from .utils import send_orders_view


router = Router()


@router.message(Command("orders"))
async def view_orders_handler(message: Message, session: AsyncSession, db_user: User):
    """Handle the /orders command to display the user's order history."""
    await send_orders_view(message, session, db_user)


@router.callback_query(OrderCallbackFactory.filter(F.action == "back_to_list"))  # type: ignore[arg-type]
async def back_to_orders_handler(
    query: CallbackQuery,
    session: AsyncSession,
    db_user: User,
    callback_message: Message,
):
    """Handle the 'Back to Order History' button click."""
    await send_orders_view(callback_message, session, db_user)
    await query.answer()


@router.callback_query(OrderCallbackFactory.filter(F.action == "list"))  # type: ignore[arg-type]
async def orders_pagination_handler(
    query: CallbackQuery,
    callback_data: OrderCallbackFactory,
    session: AsyncSession,
    db_user: User,
    callback_message: Message,
):
    """Handle pagination for the order history list."""
    page = callback_data.item_id or 1
    await send_orders_view(callback_message, session, db_user, page=page)
    await query.answer()
