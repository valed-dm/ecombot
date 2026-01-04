"""Cart item management handlers."""

from aiogram import F
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import CartCallbackFactory

from .utils import alter_cart_item


router = Router()


@router.callback_query(CartCallbackFactory.filter(F.action == "decrease"))  # type: ignore[arg-type]
async def decrease_cart_item_handler(
    query: CallbackQuery,
    callback_data: CartCallbackFactory,
    session: AsyncSession,
    callback_message: Message,
):
    """Handle decrease quantity button clicks."""
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
    """Handle increase quantity button clicks."""
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
    """Handle remove item button clicks."""
    await alter_cart_item(
        query, callback_data, session, callback_message, action="remove"
    )
