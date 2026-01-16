from aiogram import F
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ecombot.bot.callback_data import DeliveryAdminCallbackFactory
from ecombot.config import settings
from ecombot.core.manager import central_manager as manager


router = Router()


@router.message(Command("admin_delivery"))
async def cmd_admin_delivery(message: Message):
    """Entry point for delivery management."""
    await send_delivery_menu(message)


async def send_delivery_menu(target: Message | CallbackQuery):
    """Displays the main delivery management menu."""
    builder = InlineKeyboardBuilder()

    # 1. Global Delivery Toggle
    status_icon = "✅" if settings.DELIVERY else "❌"
    status_key = "enabled" if settings.DELIVERY else "disabled"
    status_text = manager.get_message("keyboards", status_key)

    builder.button(
        text=manager.get_message(
            "keyboards",
            "global_delivery_toggle",
            status_text=status_text,
            status_icon=status_icon,
        ),
        callback_data=DeliveryAdminCallbackFactory(action="toggle_global").pack(),
    )

    # 2. Management Sub-menus
    builder.button(
        text=manager.get_message("keyboards", "manage_pickup_points"),
        callback_data=DeliveryAdminCallbackFactory(action="pp_list").pack(),
    )
    builder.button(
        text=manager.get_message("keyboards", "manage_delivery_types"),
        callback_data=DeliveryAdminCallbackFactory(action="dt_list").pack(),
    )

    builder.adjust(1)

    mode_key = "mode_delivery_pickup" if settings.DELIVERY else "mode_pickup_only"
    current_mode = manager.get_message("delivery", mode_key)
    text = manager.get_message("delivery", "menu_text", current_mode=current_mode)

    if isinstance(target, Message):
        await target.answer(text, reply_markup=builder.as_markup())
    else:
        await target.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(DeliveryAdminCallbackFactory.filter(F.action == "menu"))
async def cb_back_to_menu(query: CallbackQuery):
    await send_delivery_menu(query)


@router.callback_query(DeliveryAdminCallbackFactory.filter(F.action == "toggle_global"))
async def cb_toggle_global_delivery(query: CallbackQuery):
    """Toggles the global DELIVERY setting."""
    # Note: This changes the setting in memory for the running process.
    # It does not persist to .env file.
    settings.DELIVERY = not settings.DELIVERY

    status_key = "enabled" if settings.DELIVERY else "disabled"
    status_text = manager.get_message("keyboards", status_key)
    await query.answer(
        manager.get_message("delivery", "toggled_msg", status=status_text)
    )
    await send_delivery_menu(query)
