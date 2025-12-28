"""
Handlers for the user profile and address management.
"""

from html import escape

from aiogram import F
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup
from aiogram.types import CallbackQuery
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot import keyboards
from ecombot.bot.callback_data import ProfileCallbackFactory
from ecombot.bot.middlewares import MessageInteractionMiddleware
from ecombot.db.models import User
from ecombot.logging_setup import log
from ecombot.services import user_service


# =============================================================================
# Router and Middleware Setup
# =============================================================================

router = Router()
router.callback_query.middleware(MessageInteractionMiddleware())


class EditProfile(StatesGroup):
    getting_phone = State()
    getting_email = State()


class AddAddress(StatesGroup):
    getting_label = State()
    getting_address = State()


# --- Main Profile View ---
@router.message(Command("profile"))
async def profile_handler(message: Message, session: AsyncSession, db_user: User):
    """Displays the main user profile view including the default address."""
    try:
        user_profile = await user_service.get_user_profile(session, db_user)
    except Exception as e:
        log.error(f"Failed to load profile for user {db_user.id}: {e}", exc_info=True)
        await message.answer("❌ An error occurred while loading your profile.")
        return

    default_address = next(
        (addr for addr in user_profile.addresses if addr.is_default), None
    )

    phone_text = escape(user_profile.phone) if user_profile.phone else "Not set"
    email_text = escape(user_profile.email) if user_profile.email else "Not set"

    text = (
        "<b>Your Profile</b>\n\n"
        f"<b>Name:</b> {escape(user_profile.first_name)}\n"
        f"<b>Phone:</b> {phone_text}\n"
        f"<b>Email:</b> {email_text}\n\n"
        "<b>Default Address:</b>\n"
    )
    if default_address:
        text += f"<code>{escape(default_address.full_address)}</code>"
    else:
        text += "<i>Not set. You can set one in 'Manage Addresses'.</i>"

    keyboard = keyboards.get_profile_keyboard()
    await message.answer(text, reply_markup=keyboard)


# --- Address Management ---
@router.callback_query(ProfileCallbackFactory.filter(F.action == "manage_addr"))  # type: ignore[arg-type]
async def manage_addresses_handler(
    query: CallbackQuery,
    session: AsyncSession,
    db_user: User,
    callback_message: Message,
):
    """Displays the user's saved addresses and management options."""
    await send_address_management_view(callback_message, session, db_user)
    await query.answer()


@router.callback_query(ProfileCallbackFactory.filter(F.action == "delete_addr"))  # type: ignore[arg-type]
async def delete_address_handler(
    query: CallbackQuery,
    callback_data: ProfileCallbackFactory,
    session: AsyncSession,
    db_user: User,
):
    """Handles the deletion of a specific address."""
    address_id = callback_data.address_id
    if address_id:
        try:
            await user_service.delete_address(session, db_user.id, address_id)
            await query.answer("Address deleted successfully!", show_alert=True)
            await manage_addresses_handler(query, session, db_user, query.message)
        except Exception as e:
            log.exception("Error deleting address {}", e)
            await query.answer("Failed to delete address.", show_alert=True)


@router.callback_query(ProfileCallbackFactory.filter(F.action == "set_default_addr"))  # type: ignore[arg-type]
async def set_default_address_handler(
    query: CallbackQuery,
    callback_data: ProfileCallbackFactory,
    session: AsyncSession,
    db_user: User,
    callback_message: Message,
):
    """Handles the 'Set as Default' button click."""
    address_id = callback_data.address_id
    if address_id is not None:
        try:
            await user_service.set_user_default_address(session, db_user.id, address_id)
            await query.answer("Default address updated!", show_alert=False)
            await manage_addresses_handler(query, session, db_user, callback_message)
        except Exception as e:
            log.exception(f"Error setting default address for user {db_user.id}: {e}")
            await query.answer("Failed to update default address.", show_alert=True)
    else:
        log.error(
            f"set_default_address_handler called without an address_id"
            f" for user {db_user.id}"
        )
        await query.answer(
            "An internal error occurred (missing address ID).",
            show_alert=True,
        )


@router.callback_query(F.data == "profile_back_main")
async def back_to_profile_handler(
    query: CallbackQuery,
    session: AsyncSession,
    db_user: User,
    callback_message: Message,
):
    """Handles the 'Back to Profile' button."""
    try:
        await callback_message.delete()  # Delete the address menu
    except TelegramBadRequest as e:
        log.warning(f"Failed to delete message for user {db_user.id}: {e}")

    await profile_handler(query.message, session, db_user)
    await query.answer()


# =============================================================================
# "Add Address" FSM Handlers
# =============================================================================


@router.callback_query(ProfileCallbackFactory.filter(F.action == "add_addr"))  # type: ignore[arg-type]
async def add_address_start(
    query: CallbackQuery,
    state: FSMContext,
    callback_message: Message,
):
    """Step 1 (Add Address): Asks for a label for the new address."""
    await callback_message.edit_text(
        "Let's add a new address.\n\n"
        "First, give it a short label (e.g., 'Home', 'Office').",
        reply_markup=keyboards.get_cancel_keyboard(),
    )
    await state.set_state(AddAddress.getting_label)
    await query.answer()


@router.message(AddAddress.getting_label, F.text)
async def add_address_get_label(message: Message, state: FSMContext):
    """Step 2 (Add Address): Receives the label, asks for the full address."""
    await state.update_data(label=message.text)
    await state.set_state(AddAddress.getting_address)

    try:
        await message.answer(
            "Great. Now, please enter the full shipping address.",
            reply_markup=keyboards.get_cancel_keyboard(),
        )
    except Exception as e:
        log.error(f"Failed to send address prompt: {e}", exc_info=True)


@router.message(AddAddress.getting_address, F.text)
async def add_address_get_address(
    message: Message, state: FSMContext, session: AsyncSession, db_user: User
):
    """Step 3 (Add Address): Receives the full address and saves it."""
    await state.update_data(address=message.text)
    address_data = await state.get_data()

    try:
        await user_service.add_new_address(
            session=session,
            user_id=db_user.id,
            label=address_data["label"],
            address=address_data["address"],
        )
        await message.answer("✅ New address saved successfully!")

        await send_address_management_view(message, session, db_user)

    except Exception as e:
        log.error(f"Failed to add address for user {db_user.id}: {e}", exc_info=True)
        await message.answer("❌ An error occurred while saving the address.")
    finally:
        await state.clear()


async def send_address_management_view(
    message: Message, session: AsyncSession, db_user: User
):
    """
    Sends or edits a message to show the address management view.
    """
    try:
        addresses = await user_service.get_all_user_addresses(session, db_user.id)
        keyboard = keyboards.get_address_management_keyboard(addresses)
        text = "<b>Your Delivery Addresses</b>\n\n"
        if not addresses:
            text += "You have no saved addresses."
        else:
            for addr in addresses:
                text += (
                    f"📍 <b>{escape(addr.address_label)}</b>:\n"
                    f"<code>{escape(addr.full_address)}</code>\n\n"
                )

        try:
            await message.edit_text(text, reply_markup=keyboard)
        except TelegramBadRequest as e:
            log.warning(f"Failed to edit message for user {db_user.id}: {e}")
            try:
                await message.answer(text, reply_markup=keyboard)
            except Exception as fallback_e:
                log.error(
                    f"Failed to send fallback message for user {db_user.id}: "
                    f"{fallback_e}"
                )
                raise fallback_e from e
    except Exception as e:
        log.error(f"Failed to load addresses for user {db_user.id}: {e}", exc_info=True)
        await message.answer("❌ An error occurred while loading your addresses.")


# =============================================================================
# "Edit Profile" FSM Handlers
# =============================================================================


@router.callback_query(ProfileCallbackFactory.filter(F.action == "edit_phone"))  # type: ignore[arg-type]
async def edit_phone_start(
    query: CallbackQuery,
    state: FSMContext,
    callback_message: Message,
):
    """Starts the FSM to edit the user's phone number."""
    await callback_message.edit_text(
        "Please enter your new phone number:",
        reply_markup=keyboards.get_cancel_keyboard(),
    )
    await state.set_state(EditProfile.getting_phone)
    await query.answer()


@router.message(EditProfile.getting_phone, F.text)
async def edit_phone_get_phone(
    message: Message, state: FSMContext, session: AsyncSession, db_user: User
):
    """Receives the new phone number and updates the user profile."""
    new_phone = message.text

    try:
        await user_service.update_profile_details(
            session=session, user_id=db_user.id, update_data={"phone": new_phone}
        )
        await message.answer("✅ Phone number updated successfully!")

        await session.refresh(db_user)
        await message.delete()  # Delete the "new phone number" message
        await profile_handler(message, session, db_user)

    except Exception as e:
        log.error(f"Failed to update phone for user {db_user.id}: {e}", exc_info=True)
        await message.answer("❌ An error occurred while updating your phone number.")
    finally:
        await state.clear()


@router.callback_query(ProfileCallbackFactory.filter(F.action == "edit_email"))  # type: ignore[arg-type]
async def edit_email_start(
    query: CallbackQuery,
    state: FSMContext,
    callback_message: Message,
):
    """Starts the FSM to edit the user's email address."""
    await callback_message.edit_text(
        "Please enter your new email address:",
        reply_markup=keyboards.get_cancel_keyboard(),
    )
    await state.set_state(EditProfile.getting_email)
    await query.answer()


@router.message(EditProfile.getting_email, F.text)
async def edit_email_get_email(
    message: Message, state: FSMContext, session: AsyncSession, db_user: User
):
    """Receives the new email and updates the user profile."""
    # Validation for the email can be added later.
    new_email = message.text

    try:
        await user_service.update_profile_details(
            session=session, user_id=db_user.id, update_data={"email": new_email}
        )
        await message.answer("✅ Email address updated successfully!")

        await session.refresh(db_user)
        await message.delete()  # Clean up the user's "new email" message
        await profile_handler(message, session, db_user)

    except Exception as e:
        log.error(f"Failed to update email for user {db_user.id}: {e}", exc_info=True)
        await message.answer("❌ An error occurred while updating your email address.")
    finally:
        await state.clear()
