"""Navigation handlers for profile package."""

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from ecombot.logging_setup import log

router = Router()


@router.callback_query(F.data == "do_nothing")
async def do_nothing_handler(query: CallbackQuery):
    """Handle clicks on display-only buttons."""
    await query.answer()


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