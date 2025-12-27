"""Navigation and main panel handlers."""

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from ecombot.logging_setup import log
from .helpers import send_main_admin_panel

router = Router()


@router.message(Command("cancel"), StateFilter("*"))
@router.callback_query(F.data == "cancel_fsm", StateFilter("*"))
async def cancel_fsm_handler(
    event: Message | CallbackQuery,
    state: FSMContext,
):
    """Universal handler to cancel any active FSM state for the user."""
    from aiogram.exceptions import TelegramBadRequest
    
    current_state = await state.get_state()
    if current_state is None:
        if isinstance(event, CallbackQuery):
            await event.answer("You are not in an active process.", show_alert=True)
        elif isinstance(event, Message):
            await event.answer("You are not in an active process.")
        return

    await state.clear()

    if isinstance(event, Message):
        await event.answer("Action cancelled. You have exited the current process.")
    elif isinstance(event, CallbackQuery) and isinstance(event.message, Message):
        try:
            await event.message.edit_text("Action cancelled.")
        except TelegramBadRequest as e:
            log.warning(f"Failed to edit cancellation message: {e}")
            await event.message.answer("Action cancelled.")
        await event.answer()


@router.message(Command("admin"))
async def command_admin_panel(message: Message):
    """Handler for the /admin command. Displays the main admin actions keyboard."""
    try:
        await send_main_admin_panel(message)
    except Exception as e:
        log.error(f"Failed to display admin panel: {e}", exc_info=True)
        await message.answer("❌ Failed to load admin panel. Please try again.")