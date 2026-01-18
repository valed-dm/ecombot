"""Category navigation handlers."""

from aiogram import F
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import CatalogCallbackFactory

from .utils import show_main_catalog


router = Router()


@router.message(CommandStart())
async def command_start_handler(
    message: Message, session: AsyncSession, state: FSMContext
):
    """Handler for the /start command. Displays the main product categories."""
    await show_main_catalog(message, session, state=state)


@router.callback_query(CatalogCallbackFactory.filter(F.action == "back_to_main"))  # type: ignore[arg-type]
async def back_to_main_handler(
    query: CallbackQuery,
    session: AsyncSession,
    callback_message: Message,
    state: FSMContext,
):
    """
    Handler for the "Back to Categories" button.
    Edits the current message to show the main catalog again.
    """
    await show_main_catalog(callback_message, session, is_edit=True, state=state)
    await query.answer()
