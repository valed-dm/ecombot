"""Utilities for profile handlers."""

from html import escape

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot import keyboards
from ecombot.db.models import User
from ecombot.logging_setup import log
from ecombot.services import user_service

from .states import ADDRESS_MANAGEMENT_HEADER
from .states import DEFAULT_ADDRESS_NOT_SET
from .states import ERROR_ADDRESSES_LOAD_FAILED
from .states import NO_ADDRESSES_MESSAGE
from .states import NOT_SET_TEXT
from .states import PROFILE_HEADER
from .states import PROFILE_TEMPLATE


def format_profile_text(user_profile) -> str:
    """Format the main profile view text."""
    default_address = next(
        (addr for addr in user_profile.addresses if addr.is_default), None
    )

    phone_text = escape(user_profile.phone) if user_profile.phone else NOT_SET_TEXT
    email_text = escape(user_profile.email) if user_profile.email else NOT_SET_TEXT

    text = PROFILE_HEADER + PROFILE_TEMPLATE.format(
        name=escape(user_profile.first_name), phone=phone_text, email=email_text
    )

    if default_address:
        text += f"<code>{escape(default_address.full_address)}</code>"
    else:
        text += DEFAULT_ADDRESS_NOT_SET

    return text


def format_address_management_text(addresses) -> str:
    """Format the address management view text."""
    text = ADDRESS_MANAGEMENT_HEADER
    if not addresses:
        text += NO_ADDRESSES_MESSAGE
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
        keyboard = keyboards.get_address_management_keyboard(addresses)
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
        await message.answer(ERROR_ADDRESSES_LOAD_FAILED)
