"""Category addition handlers."""

from aiogram import F
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import AdminCallbackFactory
from ecombot.bot.keyboards.common import get_cancel_keyboard
from ecombot.core.manager import central_manager as manager
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
            manager.get_message("admin_categories", "add_category_name_prompt"),
            reply_markup=get_cancel_keyboard(),
        )
    except TelegramBadRequest as e:
        log.warning(f"Failed to edit message: {e}")
        await callback_message.answer(
            manager.get_message("admin_categories", "add_category_name_prompt"),
            reply_markup=get_cancel_keyboard(),
        )
    await state.set_state(AddCategory.name)
    await query.answer()


@router.message(AddCategory.name, F.text)
async def add_category_name(message: Message, state: FSMContext):
    """Step 2: Receives the category name and asks for the description."""
    if not message.text or not message.text.strip():
        await message.answer(
            manager.get_message("admin_categories", "add_category_name_empty"),
            reply_markup=get_cancel_keyboard(),
        )
        return

    category_name = message.text.strip()
    if len(category_name) > 255:
        await message.answer(
            manager.get_message("admin_categories", "add_category_name_too_long"),
            reply_markup=get_cancel_keyboard(),
        )
        return

    await state.update_data(name=category_name)
    await message.answer(
        manager.get_message("admin_categories", "add_category_description_prompt"),
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
                manager.get_message(
                    "admin_categories", "add_category_description_too_long"
                ),
                reply_markup=get_cancel_keyboard(),
            )
            return

    try:
        new_category = await catalog_service.add_new_category(
            session=session, name=category_data["name"], description=description
        )
        await message.answer(
            manager.get_message(
                "admin_categories", "add_category_success", name=new_category.name
            )
        )
    except CategoryAlreadyExistsError as e:
        await message.answer(
            manager.get_message(
                "admin_categories", "add_category_already_exists", error=e
            )
        )
    except Exception as e:
        log.error(f"Failed to create category: {e}", exc_info=True)
        await message.answer(
            manager.get_message("admin_categories", "add_category_error")
        )
    finally:
        await state.clear()
