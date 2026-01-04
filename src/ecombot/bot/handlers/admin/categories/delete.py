"""Category deletion handlers."""

from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import AdminCallbackFactory
from ecombot.bot.callback_data import CatalogCallbackFactory
from ecombot.bot.callback_data import ConfirmationCallbackFactory
from ecombot.bot.keyboards.admin import get_admin_panel_keyboard
from ecombot.bot.keyboards.catalog import get_catalog_categories_keyboard
from ecombot.bot.keyboards.common import get_delete_confirmation_keyboard
from ecombot.db.models import Category
from ecombot.logging_setup import log
from ecombot.services import catalog_service

from .states import DeleteCategory


router = Router()


@router.callback_query(AdminCallbackFactory.filter(F.action == "delete_category"))
async def delete_category_start(
    query: CallbackQuery,
    callback_data: AdminCallbackFactory,
    session: AsyncSession,
    state: FSMContext,
    callback_message: Message,
):
    """Step 1 (Delete Cat): Starts FSM. Asks for a category."""
    try:
        categories = await catalog_service.get_all_categories(session)
    except Exception as e:
        log.error(f"Failed to load categories for delete: {e}", exc_info=True)
        await callback_message.edit_text(
            "❌ An unexpected error occurred while loading categories.",
            reply_markup=get_admin_panel_keyboard(),
        )
        await state.clear()
        await query.answer()
        return

    if not categories:
        await callback_message.edit_text(
            "❌ No categories found. You need to create at least one category "
            "before deleting categories. Please use 'Add Category' first.",
            reply_markup=get_admin_panel_keyboard(),
        )
        await query.answer()
        return

    keyboard = get_catalog_categories_keyboard(categories)
    await callback_message.edit_text(
        "Choose the category you want to delete:", reply_markup=keyboard
    )
    await state.set_state(DeleteCategory.choose_category)
    await query.answer()


@router.callback_query(
    DeleteCategory.choose_category,
    CatalogCallbackFactory.filter(F.action == "view_category"),
)
async def delete_category_confirm(
    query: CallbackQuery,
    callback_data: CatalogCallbackFactory,
    session: AsyncSession,
    state: FSMContext,
    callback_message: Message,
):
    """Step 2 (Delete Cat): Receives category, asks for confirmation."""
    category_id = callback_data.item_id
    try:
        category = await session.get(Category, category_id)
        if not category:
            await callback_message.edit_text(
                "Error: Category not found.",
                reply_markup=get_admin_panel_keyboard(),
            )
            await state.clear()
            await query.answer()
            return

        await state.update_data(category_id=category_id, category_name=category.name)
        keyboard = get_delete_confirmation_keyboard(
            action="delete_category", item_id=category_id
        )
        await callback_message.edit_text(
            f"⚠️ Are you sure you want to delete the category "
            f"'{category.name}'? It will be hidden from the catalog "
            f"but preserved in order history.",
            reply_markup=keyboard,
        )
        await state.set_state(DeleteCategory.confirm_deletion)
        await query.answer()
    except Exception as e:
        log.error(f"Failed to load category details for deletion: {e}", exc_info=True)
        await callback_message.edit_text(
            "❌ An unexpected error occurred while loading category details.",
            reply_markup=get_admin_panel_keyboard(),
        )
        await state.clear()
        await query.answer()


@router.callback_query(
    DeleteCategory.confirm_deletion,
    ConfirmationCallbackFactory.filter(F.action == "delete_category"),
)
async def delete_category_final(
    query: CallbackQuery,
    callback_data: ConfirmationCallbackFactory,
    session: AsyncSession,
    state: FSMContext,
    callback_message: Message,
):
    """Step 3 (Delete Cat): Processes the final confirmation."""
    if not callback_data.confirm:
        await callback_message.edit_text(
            "Deletion cancelled.",
            reply_markup=get_admin_panel_keyboard(),
        )
        await state.clear()
        await query.answer()
        return

    state_data = await state.get_data()
    category_name = state_data.get("category_name", "the category")

    try:
        success = await catalog_service.delete_category_by_id(
            session, callback_data.item_id
        )

        if success:
            await callback_message.edit_text(
                f"✅ Category '{category_name}' has been deleted.",
                reply_markup=get_admin_panel_keyboard(),
            )
        else:
            await callback_message.edit_text(
                f"❌ Error: Could not delete '{category_name}'."
                f" It may have already been removed.",
                reply_markup=get_admin_panel_keyboard(),
            )
    except Exception as e:
        log.error(
            f"Error deleting category {callback_data.item_id}: {e}", exc_info=True
        )
        await callback_message.edit_text(
            f"❌ An unexpected error occurred while deleting '{category_name}'.",
            reply_markup=get_admin_panel_keyboard(),
        )
    finally:
        await state.clear()
        await query.answer()
