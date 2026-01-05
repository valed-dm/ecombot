"""Category restoration handlers."""

from aiogram import F
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import AdminCallbackFactory
from ecombot.bot.callback_data import ConfirmationCallbackFactory
from ecombot.bot.keyboards.admin import get_admin_panel_keyboard
from ecombot.core.manager import central_manager as manager
from ecombot.db import crud
from ecombot.logging_setup import log
from ecombot.schemas.dto import CategoryDTO


router = Router()


@router.callback_query(AdminCallbackFactory.filter(F.action == "restore_category"))
async def restore_category_start(
    query: CallbackQuery,
    callback_data: AdminCallbackFactory,
    session: AsyncSession,
    callback_message: Message,
):
    """Shows list of deleted categories to restore."""
    try:
        deleted_categories = await crud.get_deleted_categories(session)
    except Exception as e:
        log.error(f"Failed to load deleted categories: {e}", exc_info=True)
        await callback_message.edit_text(
            manager.get_message("admin_categories", "restore_category_load_error"),
            reply_markup=get_admin_panel_keyboard(),
        )
        await query.answer()
        return

    if not deleted_categories:
        await callback_message.edit_text(
            manager.get_message("admin_categories", "restore_category_none_found"),
            reply_markup=get_admin_panel_keyboard(),
        )
        await query.answer()
        return

    # Convert to DTOs for keyboard
    category_dtos = [CategoryDTO.model_validate(cat) for cat in deleted_categories]

    # Create custom keyboard for restore selection
    builder = InlineKeyboardBuilder()
    for category in category_dtos:
        builder.button(
            text=f"🔄 {category.name}",
            callback_data=ConfirmationCallbackFactory(
                action="restore_category", item_id=category.id, confirm=True
            ),
        )
    builder.button(
        text=manager.get_message("keyboards", "back_to_admin_panel"),
        callback_data=AdminCallbackFactory(action="back_main"),
    )
    builder.adjust(1)
    keyboard = builder.as_markup()

    await callback_message.edit_text(
        manager.get_message("admin_categories", "restore_category_choose_prompt"),
        reply_markup=keyboard,
    )
    await query.answer()


@router.callback_query(
    ConfirmationCallbackFactory.filter(F.action == "restore_category")
)
async def restore_category_confirm(
    query: CallbackQuery,
    callback_data: ConfirmationCallbackFactory,
    session: AsyncSession,
    callback_message: Message,
):
    """Restores the selected category."""
    category_id = callback_data.item_id

    try:
        success = await crud.restore_category(session, category_id)

        if success:
            await callback_message.edit_text(
                manager.get_message("admin_categories", "restore_category_success"),
                reply_markup=get_admin_panel_keyboard(),
            )
        else:
            await callback_message.edit_text(
                manager.get_message("admin_categories", "restore_category_not_found"),
                reply_markup=get_admin_panel_keyboard(),
            )
    except Exception as e:
        log.error(f"Error restoring category {category_id}: {e}", exc_info=True)
        await callback_message.edit_text(
            manager.get_message("admin_categories", "restore_category_error"),
            reply_markup=get_admin_panel_keyboard(),
        )

    await query.answer()
