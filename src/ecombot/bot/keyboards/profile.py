"""Profile-related keyboards."""

from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ecombot.schemas.dto import DeliveryAddressDTO

from ..callback_data import ProfileCallbackFactory


def get_profile_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📞 Edit Phone",
        callback_data=ProfileCallbackFactory(action="edit_phone"),
    )
    builder.button(
        text="✉️ Edit Email",
        callback_data=ProfileCallbackFactory(action="edit_email"),
    )
    builder.button(
        text="📍 Manage Addresses",
        callback_data=ProfileCallbackFactory(action="manage_addr"),
    )
    builder.adjust(2, 1)
    return builder.as_markup()


def get_address_details_keyboard() -> InlineKeyboardMarkup:
    """Builds a keyboard for address details view."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⬅️ Back to Addresses",
        callback_data=ProfileCallbackFactory(action="manage_addr"),
    )
    return builder.as_markup()


def get_address_management_keyboard(
    addresses: list[DeliveryAddressDTO],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for addr in addresses:
        # Add a star for the default address
        prefix = "⭐️ Default: " if addr.is_default else "📍"

        builder.row(
            InlineKeyboardButton(
                text=f"{prefix} {addr.address_label}",
                callback_data=ProfileCallbackFactory(
                    action="view_addr", address_id=addr.id
                ).pack(),
            )
        )
        action_row = (
            [
                InlineKeyboardButton(
                    text="Set as Default",
                    callback_data=ProfileCallbackFactory(
                        action="set_default_addr", address_id=addr.id
                    ).pack(),
                )
            ]
            if not addr.is_default
            else []
        ) + [
            InlineKeyboardButton(
                text="❌ Delete",
                callback_data=ProfileCallbackFactory(
                    action="delete_addr", address_id=addr.id
                ).pack(),
            )
        ]
        builder.row(*action_row)

    builder.button(
        text="➕ Add New Address",
        callback_data=ProfileCallbackFactory(action="add_addr"),
    )
    builder.button(
        text="⬅️ Back to Profile",
        callback_data=ProfileCallbackFactory(action="profile_back_main"),
    )
    return builder.as_markup()
