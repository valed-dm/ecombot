"""Navigation handlers for admin orders."""

from aiogram import F
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.types import Message

from ecombot.bot.callback_data import AdminCallbackFactory
from ecombot.bot.handlers.admin.helpers import send_main_admin_panel


router = Router()


@router.callback_query(AdminCallbackFactory.filter(F.action == "back_main"))  # type: ignore[arg-type]
async def back_to_main_admin_panel_handler(
    query: CallbackQuery, callback_message: Message
):
    """Handle the "Back to Admin Panel" button from any order management view."""
    await send_main_admin_panel(callback_message)
    await query.answer()
