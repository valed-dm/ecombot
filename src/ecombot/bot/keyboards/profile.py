"""Profile-related keyboards."""

from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ecombot.core.manager import central_manager as manager
from ecombot.schemas.dto import DeliveryAddressDTO

from ..callback_data import ProfileCallbackFactory


def get_profile_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=manager.get_message("keyboards", "edit_phone"),
        callback_data=ProfileCallbackFactory(action="edit_phone"),
    )
    builder.button(
        text=manager.get_message("keyboards", "edit_email"),
        callback_data=ProfileCallbackFactory(action="edit_email"),
    )
    builder.button(
        text=manager.get_message("keyboards", "manage_addresses"),
        callback_data=ProfileCallbackFactory(action="manage_addr"),
    )
    builder.adjust(1)
    return builder.as_markup()


def get_address_details_keyboard() -> InlineKeyboardMarkup:
    """Builds a keyboard for address details view."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text=manager.get_message("keyboards", "back_to_addresses"),
        callback_data=ProfileCallbackFactory(action="manage_addr"),
    )
    return builder.as_markup()


def get_address_management_keyboard(
    addresses: list[DeliveryAddressDTO],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for addr in addresses:
        # Localized prefix using profile messages
        prefix = (
            manager.get_message("profile", "default_address_prefix")
            if addr.is_default
            else manager.get_message("profile", "address_prefix")
        )

        builder.row(
            InlineKeyboardButton(
                text=f"{prefix} {addr.address_label}",
                callback_data=ProfileCallbackFactory(
                    action="view_addr", address_id=addr.id
                ).pack(),
            )
        )
        if not addr.is_default:
            builder.row(
                InlineKeyboardButton(
                    text=manager.get_message("keyboards", "set_as_default"),
                    callback_data=ProfileCallbackFactory(
                        action="set_default_addr", address_id=addr.id
                    ).pack(),
                )
            )
        builder.row(
            InlineKeyboardButton(
                text=manager.get_message("keyboards", "delete_address"),
                callback_data=ProfileCallbackFactory(
                    action="delete_addr", address_id=addr.id
                ).pack(),
            )
        )

    builder.button(
        text=manager.get_message("keyboards", "add_address"),
        callback_data=ProfileCallbackFactory(action="add_addr"),
    )
    builder.button(
        text=manager.get_message("keyboards", "back_to_profile"),
        callback_data=ProfileCallbackFactory(action="profile_back_main"),
    )
    builder.adjust(1)
    return builder.as_markup()
