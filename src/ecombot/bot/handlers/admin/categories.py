"""Category management handlers."""

from aiogram import F
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot import keyboards
from ecombot.bot.callback_data import AdminCallbackFactory
from ecombot.bot.callback_data import CatalogCallbackFactory
from ecombot.bot.callback_data import ConfirmationCallbackFactory
from ecombot.db.models import Category
from ecombot.logging_setup import log
from ecombot.services import catalog_service
from ecombot.services.catalog_service import CategoryAlreadyExistsError
from ecombot.services.catalog_service import CategoryNotEmptyError

from .states import AddCategory
from .states import DeleteCategory


router = Router()


@router.callback_query(AdminCallbackFactory.filter(F.action == "add_category"))  # type: ignore[arg-type]
async def add_category_start(
    query: CallbackQuery,
    callback_data: AdminCallbackFactory,
    state: FSMContext,
    callback_message: Message,
):
    """Step 1: Starts the Add Category FSM. Asks for the category name."""
    try:
        await callback_message.edit_text(
            "Please enter the name for the new category:",
            reply_markup=keyboards.get_cancel_keyboard(),
        )
    except TelegramBadRequest as e:
        log.warning(f"Failed to edit message: {e}")
        await callback_message.answer(
            "Please enter the name for the new category:",
            reply_markup=keyboards.get_cancel_keyboard(),
        )
    await state.set_state(AddCategory.name)
    await query.answer()


@router.message(AddCategory.name, F.text)
async def add_category_name(message: Message, state: FSMContext):
    """Step 2: Receives the category name and asks for the description."""
    if not message.text or not message.text.strip():
        await message.answer(
            "Please enter a valid category name (cannot be empty).",
            reply_markup=keyboards.get_cancel_keyboard(),
        )
        return

    category_name = message.text.strip()
    if len(category_name) > 255:
        await message.answer(
            "Category name is too long (maximum 255 characters).",
            reply_markup=keyboards.get_cancel_keyboard(),
        )
        return

    await state.update_data(name=category_name)
    await message.answer(
        "Great. Now enter a description for the category (or send /skip):",
        reply_markup=keyboards.get_cancel_keyboard(),
    )
    await state.set_state(AddCategory.description)


@router.message(AddCategory.description, or_f(F.text, Command("skip")))
async def add_category_description(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Step 3: Receives the description (or /skip) and creates the category."""
    category_data = await state.get_data()
    description = message.text if message.text != "/skip" else None

    if description is not None:
        description = description.strip()
        if not description:
            description = None
        elif len(description) > 1000:
            await message.answer(
                "Description is too long (maximum 1000 characters).",
                reply_markup=keyboards.get_cancel_keyboard(),
            )
            return

    try:
        new_category = await catalog_service.add_new_category(
            session=session, name=category_data["name"], description=description
        )
        await message.answer(f"✅ Category '{new_category.name}' created successfully!")
    except CategoryAlreadyExistsError as e:
        await message.answer(f"⚠️ Error: {e}")
    except Exception as e:
        log.error(f"Failed to create category: {e}", exc_info=True)
        await message.answer(
            "❌ An unexpected error occurred while creating the category."
        )
    finally:
        await state.clear()


@router.callback_query(AdminCallbackFactory.filter(F.action == "delete_category"))  # type: ignore[arg-type]
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
            reply_markup=keyboards.get_admin_panel_keyboard(),
        )
        await state.clear()
        await query.answer()
        return

    if not categories:
        await callback_message.edit_text(
            "❌ No categories found. You need to create at least one category "
            "before deleting categories. Please use 'Add Category' first.",
            reply_markup=keyboards.get_admin_panel_keyboard(),
        )
        await query.answer()
        return

    keyboard = keyboards.get_catalog_categories_keyboard(categories)
    await callback_message.edit_text(
        "Choose the category you want to delete:", reply_markup=keyboard
    )
    await state.set_state(DeleteCategory.choose_category)
    await query.answer()


@router.callback_query(
    DeleteCategory.choose_category,
    CatalogCallbackFactory.filter(F.action == "view_category"),  # type: ignore[arg-type]
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
                reply_markup=keyboards.get_admin_panel_keyboard(),
            )
            await state.clear()
            await query.answer()
            return

        await state.update_data(category_id=category_id, category_name=category.name)
        keyboard = keyboards.get_delete_confirmation_keyboard(
            action="delete_category", item_id=category_id
        )
        await callback_message.edit_text(
            f"⚠️ Are you sure you want to permanently delete the category "
            f"'{category.name}'?",
            reply_markup=keyboard,
        )
        await state.set_state(DeleteCategory.confirm_deletion)
        await query.answer()
    except Exception as e:
        log.error(f"Failed to load category details for deletion: {e}", exc_info=True)
        await callback_message.edit_text(
            "❌ An unexpected error occurred while loading category details.",
            reply_markup=keyboards.get_admin_panel_keyboard(),
        )
        await state.clear()
        await query.answer()


@router.callback_query(
    DeleteCategory.confirm_deletion,
    ConfirmationCallbackFactory.filter(F.action == "delete_category"),  # type: ignore[arg-type]
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
            reply_markup=keyboards.get_admin_panel_keyboard(),
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
                reply_markup=keyboards.get_admin_panel_keyboard(),
            )
        else:
            await callback_message.edit_text(
                f"❌ Error: Could not delete '{category_name}'."
                f" It may have already been removed.",
                reply_markup=keyboards.get_admin_panel_keyboard(),
            )
    except CategoryNotEmptyError:
        await callback_message.edit_text(
            f"❌ Cannot delete '{category_name}' because it still"
            f" contains products. Please move or delete them first.",
            reply_markup=keyboards.get_admin_panel_keyboard(),
        )
    except Exception as e:
        log.error(
            f"Error deleting category {callback_data.item_id}: {e}", exc_info=True
        )
        await callback_message.edit_text(
            "An unexpected error occurred.",
            reply_markup=keyboards.get_admin_panel_keyboard(),
        )

    await state.clear()
    await query.answer()
