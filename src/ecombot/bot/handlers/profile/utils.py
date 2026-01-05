"""Utilities for profile handlers."""

from html import escape

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.keyboards.profile import get_address_management_keyboard
from ecombot.core.manager import central_manager as manager
from ecombot.db.models import User
from ecombot.logging_setup import log
from ecombot.services import user_service


def format_profile_text(user_profile) -> str:
    """Format the main profile view text."""
    default_address = next(
        (addr for addr in user_profile.addresses if addr.is_default), None
    )

    phone_text = (
        escape(user_profile.phone)
        if user_profile.phone
        else manager.get_message("profile", "not_set_text")
    )
    email_text = (
        escape(user_profile.email)
        if user_profile.email
        else manager.get_message("profile", "not_set_text")
    )

    text = manager.get_message("profile", "profile_header") + manager.get_message(
        "profile",
        "profile_template",
        name=escape(user_profile.first_name),
        phone=phone_text,
        email=email_text,
    )

    if default_address:
        text += f"<code>{escape(default_address.full_address)}</code>"
    else:
        text += manager.get_message("profile", "default_address_not_set")

    return text


def format_address_management_text(addresses) -> str:
    """Format the address management view text."""
    text = manager.get_message("profile", "address_management_header")
    if not addresses:
        text += manager.get_message("profile", "no_addresses_message")
    else:
        for addr in addresses:
            text += (
                f"📍 <b>{escape(addr.address_label)}</b>:\n"
                f"<code>{escape(addr.full_address)}</code>\n\n"
            )
    return text


async def send_address_management_view(
    message: Message, session: AsyncSession, db_user: User
):
    """Send or edit a message to show the address management view."""
    try:
        addresses = await user_service.get_all_user_addresses(session, db_user.id)
        keyboard = get_address_management_keyboard(addresses)
        text = format_address_management_text(addresses)

        try:
            await message.edit_text(text, reply_markup=keyboard)
        except TelegramBadRequest as e:
            if "message is not modified" in e.message:
                # Message content is the same, no need to update
                return
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
        await message.answer(
            manager.get_message("profile", "error_addresses_load_failed")
        )
