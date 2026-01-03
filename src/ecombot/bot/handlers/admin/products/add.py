"""Add product workflow handlers."""

import decimal
import uuid
from decimal import Decimal
from pathlib import Path

from aiogram import Bot
from aiogram import F
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.types import PhotoSize
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot import keyboards
from ecombot.bot.callback_data import AdminCallbackFactory
from ecombot.bot.callback_data import CatalogCallbackFactory
from ecombot.config import settings
from ecombot.logging_setup import log
from ecombot.services import catalog_service

from ..states import AddProduct


router = Router()


@router.callback_query(AdminCallbackFactory.filter(F.action == "add_product"))  # type: ignore[arg-type]
async def add_product_start(
    event: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    callback_data: AdminCallbackFactory,
):
    """Step 1: Starts the Add Product FSM. Asks the admin to choose a category."""
    try:
        categories = await catalog_service.get_all_categories(session)
    except Exception as e:
        log.error(f"Failed to fetch categories: {e}", exc_info=True)
        text = "❌ Failed to load categories. Please try again."
        if isinstance(event.message, Message):
            await event.message.edit_text(text)
            await event.answer()
        return

    if not categories:
        text = (
            "❌ No categories found. You need to create at least one category "
            "before adding products. Please use 'Add Category' first."
        )
        if isinstance(event.message, Message):
            await event.message.edit_text(text)
            await event.answer()
        return

    keyboard = keyboards.get_catalog_categories_keyboard(categories)
    text = "Please choose the category for the new product:"

    if isinstance(event.message, Message):
        await event.message.edit_text(text, reply_markup=keyboard)
        await event.answer()

    await state.set_state(AddProduct.choose_category)


@router.callback_query(
    AddProduct.choose_category,
    CatalogCallbackFactory.filter(F.action == "view_category"),  # type: ignore[arg-type]
)
async def add_product_choose_category(
    query: CallbackQuery,
    callback_data: CatalogCallbackFactory,
    state: FSMContext,
    callback_message: Message,
):
    """Step 2: Receives the category and asks for the product name."""
    await state.update_data(category_id=callback_data.item_id)
    try:
        await callback_message.edit_text(
            "Great. Now, what is the name of the product?",
            reply_markup=keyboards.get_cancel_keyboard(),
        )
    except TelegramBadRequest as e:
        log.warning(f"Failed to edit message: {e}")
        await callback_message.answer(
            "Great. Now, what is the name of the product?",
            reply_markup=keyboards.get_cancel_keyboard(),
        )
    await state.set_state(AddProduct.name)
    await query.answer()


@router.message(AddProduct.name, F.text)
async def add_product_name(message: Message, state: FSMContext):
    """Step 3: Receives the product name and asks for the description."""
    if not message.text or not message.text.strip():
        await message.answer(
            "Please enter a valid product name (cannot be empty).",
            reply_markup=keyboards.get_cancel_keyboard(),
        )
        return

    product_name = message.text.strip()
    if len(product_name) > 255:
        await message.answer(
            "Product name is too long (maximum 255 characters).",
            reply_markup=keyboards.get_cancel_keyboard(),
        )
        return

    await state.update_data(name=product_name)
    await message.answer(
        "Got it. Now, please provide a description for the product.",
        reply_markup=keyboards.get_cancel_keyboard(),
    )
    await state.set_state(AddProduct.description)


@router.message(AddProduct.description, F.text)
async def add_product_description_step(message: Message, state: FSMContext):
    """Step 4: Receives the product description and asks for the price."""
    if not message.text or not message.text.strip():
        await message.answer(
            "Please enter a valid product description (cannot be empty).",
            reply_markup=keyboards.get_cancel_keyboard(),
        )
        return

    product_description = message.text.strip()
    if len(product_description) > 1000:
        await message.answer(
            "Product description is too long (maximum 1000 characters).",
            reply_markup=keyboards.get_cancel_keyboard(),
        )
        return

    await state.update_data(description=product_description)
    await message.answer(
        "Excellent. What is the price? (e.g., 25.99)",
        reply_markup=keyboards.get_cancel_keyboard(),
    )
    await state.set_state(AddProduct.price)


@router.message(AddProduct.price, F.text)
async def add_product_price_step(message: Message, state: FSMContext):
    """Step 5: Receives the price, validates it, and asks for the stock quantity."""
    try:
        price = Decimal(message.text)
        if price <= 0:
            await message.answer(
                "Price must be a positive number. Please try again.",
                reply_markup=keyboards.get_cancel_keyboard(),
            )
            return
    except decimal.InvalidOperation:
        await message.answer(
            "Invalid price format. Please enter a number (e.g., 25.99).",
            reply_markup=keyboards.get_cancel_keyboard(),
        )
        return

    await state.update_data(price=price)
    await message.answer(
        "Good. Now, how many units are in stock? (e.g., 50)",
        reply_markup=keyboards.get_cancel_keyboard(),
    )
    await state.set_state(AddProduct.stock)


@router.message(AddProduct.stock, F.text)
async def add_product_stock_step(message: Message, state: FSMContext):
    """Step 6: Receives the stock, validates it, and asks for the product image."""
    if not message.text:
        await message.answer(
            "Please send the stock quantity as text, not a photo or sticker."
        )
        return

    try:
        stock = int(message.text)
        if stock < 0:
            await message.answer(
                "Stock cannot be negative. Please enter a whole number.",
                reply_markup=keyboards.get_cancel_keyboard(),
            )
            return
    except ValueError:
        await message.answer(
            "Invalid format. Please enter a whole number.",
            reply_markup=keyboards.get_cancel_keyboard(),
        )
        return

    await state.update_data(stock=stock)
    await message.answer(
        "Excellent. Now, please upload a photo for the product (or send /skip).",
        reply_markup=keyboards.get_cancel_keyboard(),
    )
    await state.set_state(AddProduct.get_image)


@router.message(AddProduct.get_image, or_f(F.photo, Command("skip")))
async def add_product_get_image(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot,
):
    """Step 7 (Final): Receives the photo (or /skip) and creates the product."""
    image_path: str | None = None
    if message.photo:
        photo: PhotoSize = message.photo[-1]
        settings.PRODUCT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        unique_filename = f"{uuid.uuid4()}.jpg"
        destination = settings.PRODUCT_IMAGE_DIR / unique_filename
        await bot.download(file=photo.file_id, destination=destination)
        image_path = str(destination)

    await state.update_data(image_url=image_path)
    product_data = await state.get_data()

    try:
        new_product = await catalog_service.add_new_product(
            session=session,
            name=product_data["name"],
            description=product_data["description"],
            price=product_data["price"],
            stock=product_data["stock"],
            category_id=product_data["category_id"],
            image_url=product_data["image_url"],
        )
        await message.answer(f"✅ Product '{new_product.name}' created successfully!")

    except Exception as e:
        if image_path:
            try:
                Path(image_path).unlink()
                log.info(f"Cleaned up orphaned image file: {image_path}")
            except OSError as cleanup_e:
                log.error(f"Failed to cleanup image file {image_path}: {cleanup_e}")
        admin_id: str = "Unknown"
        if message.from_user:
            admin_id = str(message.from_user.id)
        log.error(
            f"Failed to create product. Admin: {admin_id}. Error: {e}",
            exc_info=True,
        )
        await message.answer(
            "❌ An unexpected error occurred while creating the product. "
            "Please check the logs for details."
        )
    finally:
        await state.clear()
