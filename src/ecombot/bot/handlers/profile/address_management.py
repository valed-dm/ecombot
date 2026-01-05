"""Address management handlers."""

from html import escape

from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import ProfileCallbackFactory
from ecombot.bot.keyboards.common import get_cancel_keyboard
from ecombot.bot.keyboards.profile import get_address_details_keyboard
from ecombot.core.manager import central_manager as manager
from ecombot.db.models import User
from ecombot.logging_setup import log
from ecombot.services import user_service

from .states import AddAddress
from .utils import send_address_management_view


router = Router()


@router.callback_query(ProfileCallbackFactory.filter(F.action == "view_addr"))  # type: ignore[arg-type]
async def view_address_handler(
    query: CallbackQuery,
    callback_data: ProfileCallbackFactory,
    session: AsyncSession,
    db_user: User,
    callback_message: Message,
):
    """Handle viewing a specific address details."""
    address_id = callback_data.address_id
    if not address_id:
        await query.answer(
            manager.get_message("profile", "address_not_found"), show_alert=True
        )
        return

    try:
        addresses = await user_service.get_all_user_addresses(session, db_user.id)
        address = next((addr for addr in addresses if addr.id == address_id), None)

        if not address:
            await query.answer(
                manager.get_message("profile", "address_not_found"), show_alert=True
            )
            return

        prefix = (
            manager.get_message("profile", "default_address_prefix")
            if address.is_default
            else manager.get_message("profile", "address_prefix")
        )
        text = (
            f"<b>{prefix}</b>\n\n"
            f"{manager.get_message(
                'profile', 'address_label_field',
                label=escape(address.address_label)
            )}\n\n"
            f"{manager.get_message(
                'profile', 'address_full_field',
                address=escape(address.full_address)
            )}"
        )

        keyboard = get_address_details_keyboard()
        await callback_message.edit_text(text, reply_markup=keyboard)
        await query.answer()

    except Exception as e:
        log.error(
            f"Failed to load address details for user {db_user.id}: {e}",
            exc_info=True,
        )
        await query.answer(
            manager.get_message("profile", "failed_load_address_details"),
            show_alert=True,
        )


@router.callback_query(ProfileCallbackFactory.filter(F.action == "manage_addr"))  # type: ignore[arg-type]
async def manage_addresses_handler(
    query: CallbackQuery,
    session: AsyncSession,
    db_user: User,
    callback_message: Message,
):
    """Display the user's saved addresses and management options."""
    await send_address_management_view(callback_message, session, db_user)
    await query.answer()


@router.callback_query(ProfileCallbackFactory.filter(F.action == "delete_addr"))  # type: ignore[arg-type]
async def delete_address_handler(
    query: CallbackQuery,
    callback_data: ProfileCallbackFactory,
    session: AsyncSession,
    db_user: User,
    callback_message: Message,
):
    """Handle the deletion of a specific address."""
    address_id = callback_data.address_id
    if address_id:
        try:
            await user_service.delete_address(session, db_user.id, address_id)
            await query.answer(
                manager.get_message("profile", "success_address_deleted"),
                show_alert=True,
            )
            await send_address_management_view(callback_message, session, db_user)
        except Exception as e:
            log.exception("Error deleting address {}", e)
            await query.answer(
                manager.get_message("profile", "error_address_delete_failed"),
                show_alert=True,
            )


@router.callback_query(ProfileCallbackFactory.filter(F.action == "set_default_addr"))  # type: ignore[arg-type]
async def set_default_address_handler(
    query: CallbackQuery,
    callback_data: ProfileCallbackFactory,
    session: AsyncSession,
    db_user: User,
    callback_message: Message,
):
    """Handle the 'Set as Default' button click."""
    address_id = callback_data.address_id
    if address_id is not None:
        try:
            await user_service.set_user_default_address(session, db_user.id, address_id)
            await query.answer(
                manager.get_message("profile", "success_default_address_updated"),
                show_alert=False,
            )
            await send_address_management_view(callback_message, session, db_user)
        except Exception as e:
            log.exception(f"Error setting default address for user {db_user.id}: {e}")
            await query.answer(
                manager.get_message("profile", "error_default_address_failed"),
                show_alert=True,
            )
    else:
        log.error(
            f"set_default_address_handler called without an address_id"
            f" for user {db_user.id}"
        )
        await query.answer(
            manager.get_message("profile", "error_missing_address_id"),
            show_alert=True,
        )


@router.callback_query(ProfileCallbackFactory.filter(F.action == "add_addr"))  # type: ignore[arg-type]
async def add_address_start(
    query: CallbackQuery,
    state: FSMContext,
    callback_message: Message,
):
    """Step 1 (Add Address): Ask for a label for the new address."""
    await callback_message.edit_text(
        manager.get_message("profile", "add_address_start_prompt"),
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(AddAddress.getting_label)
    await query.answer()


@router.message(AddAddress.getting_label, F.text)
async def add_address_get_label(message: Message, state: FSMContext):
    """Step 2 (Add Address): Receive the label, ask for the full address."""
    await state.update_data(label=message.text)
    await state.set_state(AddAddress.getting_address)

    try:
        await message.answer(
            manager.get_message("profile", "add_address_full_prompt"),
            reply_markup=get_cancel_keyboard(),
        )
    except Exception as e:
        log.error(f"Failed to send address prompt: {e}", exc_info=True)


@router.message(AddAddress.getting_address, F.text)
async def add_address_get_address(
    message: Message, state: FSMContext, session: AsyncSession, db_user: User
):
    """Step 3 (Add Address): Receive the full address and save it."""
    await state.update_data(address=message.text)
    address_data = await state.get_data()

    try:
        await user_service.add_new_address(
            session=session,
            user_id=db_user.id,
            label=address_data["label"],
            address=address_data["address"],
        )
        await message.answer(manager.get_message("profile", "success_address_saved"))

        await send_address_management_view(message, session, db_user)

    except Exception as e:
        log.error(f"Failed to add address for user {db_user.id}: {e}", exc_info=True)
        await message.answer(
            manager.get_message("profile", "error_address_save_failed")
        )
    finally:
        await state.clear()
