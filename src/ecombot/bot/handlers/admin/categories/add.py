"""Category addition handlers."""

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import AdminCallbackFactory
from ecombot.bot.keyboards.common import get_cancel_keyboard
from ecombot.logging_setup import log
from ecombot.services import catalog_service
from ecombot.services.catalog_service import CategoryAlreadyExistsError

from .states import AddCategory

router = Router()


@router.callback_query(AdminCallbackFactory.filter(F.action == "add_category"))
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
            reply_markup=get_cancel_keyboard(),
        )
    except TelegramBadRequest as e:
        log.warning(f"Failed to edit message: {e}")
        await callback_message.answer(
            "Please enter the name for the new category:",
            reply_markup=get_cancel_keyboard(),
        )
    await state.set_state(AddCategory.name)
    await query.answer()


@router.message(AddCategory.name, F.text)
async def add_category_name(message: Message, state: FSMContext):
    """Step 2: Receives the category name and asks for the description."""
    if not message.text or not message.text.strip():
        await message.answer(
            "Please enter a valid category name (cannot be empty).",
            reply_markup=get_cancel_keyboard(),
        )
        return

    category_name = message.text.strip()
    if len(category_name) > 255:
        await message.answer(
            "Category name is too long (maximum 255 characters).",
            reply_markup=get_cancel_keyboard(),
        )
        return

    await state.update_data(name=category_name)
    await message.answer(
        "Great. Now enter a description for the category (or send /skip):",
        reply_markup=get_cancel_keyboard(),
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
                reply_markup=get_cancel_keyboard(),
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