"""Product restoration handlers."""

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
from ecombot.schemas.dto import ProductDTO


router = Router()


@router.callback_query(AdminCallbackFactory.filter(F.action == "restore_product"))
async def restore_product_start(
    query: CallbackQuery,
    callback_data: AdminCallbackFactory,
    session: AsyncSession,
    callback_message: Message,
):
    """Shows list of deleted products to restore."""
    try:
        deleted_products = await crud.get_deleted_products(session)
    except Exception as e:
        log.error(f"Failed to load deleted products: {e}", exc_info=True)
        await callback_message.edit_text(
            manager.get_message("admin_products", "restore_product_load_error"),
            reply_markup=get_admin_panel_keyboard(),
        )
        await query.answer()
        return

    if not deleted_products:
        await callback_message.edit_text(
            manager.get_message("admin_products", "restore_product_none_found"),
            reply_markup=get_admin_panel_keyboard(),
        )
        await query.answer()
        return

    # Convert to DTOs for keyboard
    product_dtos = [ProductDTO.model_validate(prod) for prod in deleted_products]

    # Create custom keyboard for restore selection
    builder = InlineKeyboardBuilder()
    for product in product_dtos:
        builder.button(
            text=manager.get_message(
                "common",
                "restore_product_template",
                name=product.name,
                price=product.price,
            ),
            callback_data=ConfirmationCallbackFactory(
                action="restore_product", item_id=product.id, confirm=True
            ),
        )
    builder.button(
        text=manager.get_message("common", "back_to_admin"),
        callback_data=AdminCallbackFactory(action="back_main"),
    )
    builder.adjust(1)
    keyboard = builder.as_markup()

    await callback_message.edit_text(
        manager.get_message("admin_products", "restore_product_choose_prompt"),
        reply_markup=keyboard,
    )
    await query.answer()


@router.callback_query(
    ConfirmationCallbackFactory.filter(F.action == "restore_product")
)
async def restore_product_confirm(
    query: CallbackQuery,
    callback_data: ConfirmationCallbackFactory,
    session: AsyncSession,
    callback_message: Message,
):
    """Restores the selected product."""
    product_id = callback_data.item_id

    try:
        success = await crud.restore_product(session, product_id)

        if success:
            await callback_message.edit_text(
                manager.get_message("admin_products", "restore_product_success"),
                reply_markup=get_admin_panel_keyboard(),
            )
        else:
            await callback_message.edit_text(
                manager.get_message("admin_products", "restore_product_not_found"),
                reply_markup=get_admin_panel_keyboard(),
            )
    except Exception as e:
        log.error(f"Error restoring product {product_id}: {e}", exc_info=True)
        await callback_message.edit_text(
            manager.get_message("admin_products", "restore_product_unexpected_error"),
            reply_markup=get_admin_panel_keyboard(),
        )

    await query.answer()
