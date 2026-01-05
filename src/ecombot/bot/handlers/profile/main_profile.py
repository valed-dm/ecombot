"""Main profile viewing and editing handlers."""

from aiogram import F
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import ProfileCallbackFactory
from ecombot.bot.keyboards.common import get_cancel_keyboard
from ecombot.bot.keyboards.profile import get_profile_keyboard
from ecombot.core.manager import central_manager as manager
from ecombot.db.models import User
from ecombot.logging_setup import log
from ecombot.services import user_service

from .states import EditProfile
from .utils import format_profile_text


router = Router()


@router.message(Command("profile"))
async def profile_handler(message: Message, session: AsyncSession, db_user: User):
    """Display the main user profile view including the default address."""
    try:
        user_profile = await user_service.get_user_profile(session, db_user)
    except Exception as e:
        log.error(f"Failed to load profile for user {db_user.id}: {e}", exc_info=True)
        await message.answer(
            manager.get_message("profile", "error_profile_load_failed")
        )
        return

    text = format_profile_text(user_profile)
    keyboard = get_profile_keyboard()
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data == "profile_back_main")
async def back_to_profile_handler(
    query: CallbackQuery,
    session: AsyncSession,
    db_user: User,
    callback_message: Message,
):
    """Handle the 'Back to Profile' button."""
    try:
        user_profile = await user_service.get_user_profile(session, db_user)
        text = format_profile_text(user_profile)
        keyboard = get_profile_keyboard()
        await callback_message.edit_text(text, reply_markup=keyboard)
    except Exception as e:
        log.error(f"Failed to load profile for user {db_user.id}: {e}", exc_info=True)
        await callback_message.edit_text(
            manager.get_message("profile", "error_profile_load_failed")
        )

    await query.answer()


@router.callback_query(ProfileCallbackFactory.filter(F.action == "edit_phone"))  # type: ignore[arg-type]
async def edit_phone_start(
    query: CallbackQuery,
    state: FSMContext,
    callback_message: Message,
):
    """Start the FSM to edit the user's phone number."""
    await callback_message.edit_text(
        manager.get_message("profile", "edit_phone_prompt"),
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(EditProfile.getting_phone)
    await query.answer()


@router.message(EditProfile.getting_phone, F.text)
async def edit_phone_get_phone(
    message: Message, state: FSMContext, session: AsyncSession, db_user: User
):
    """Receive the new phone number and update the user profile."""
    new_phone = message.text

    try:
        await user_service.update_profile_details(
            session=session, user_id=db_user.id, update_data={"phone": new_phone}
        )
        await message.answer(manager.get_message("profile", "success_phone_updated"))

        await session.refresh(db_user)
        await message.delete()  # Delete the "new phone number" message
        await profile_handler(message, session, db_user)

    except Exception as e:
        log.error(f"Failed to update phone for user {db_user.id}: {e}", exc_info=True)
        await message.answer(
            manager.get_message("profile", "error_phone_update_failed")
        )
    finally:
        await state.clear()


@router.callback_query(ProfileCallbackFactory.filter(F.action == "edit_email"))  # type: ignore[arg-type]
async def edit_email_start(
    query: CallbackQuery,
    state: FSMContext,
    callback_message: Message,
):
    """Start the FSM to edit the user's email address."""
    await callback_message.edit_text(
        manager.get_message("profile", "edit_email_prompt"),
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(EditProfile.getting_email)
    await query.answer()


@router.message(EditProfile.getting_email, F.text)
async def edit_email_get_email(
    message: Message, state: FSMContext, session: AsyncSession, db_user: User
):
    """Receive the new email and update the user profile."""
    # Validation for the email can be added later.
    new_email = message.text

    try:
        await user_service.update_profile_details(
            session=session, user_id=db_user.id, update_data={"email": new_email}
        )
        await message.answer(manager.get_message("profile", "success_email_updated"))

        await session.refresh(db_user)
        await message.delete()  # Clean up the user's "new email" message
        await profile_handler(message, session, db_user)

    except Exception as e:
        log.error(f"Failed to update email for user {db_user.id}: {e}", exc_info=True)
        await message.answer(
            manager.get_message("profile", "error_email_update_failed")
        )
    finally:
        await state.clear()
