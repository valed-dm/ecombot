"""Add product workflow handlers."""

import decimal
from decimal import Decimal
from pathlib import Path
import uuid

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

from ecombot.bot.callback_data import AddProductImageCallbackFactory
from ecombot.bot.callback_data import AdminCallbackFactory
from ecombot.bot.callback_data import CatalogCallbackFactory
from ecombot.bot.keyboards.admin import get_add_product_image_keyboard
from ecombot.bot.keyboards.catalog import get_catalog_categories_keyboard
from ecombot.bot.keyboards.common import get_cancel_keyboard
from ecombot.config import settings
from ecombot.core.manager import central_manager as manager
from ecombot.logging_setup import log
from ecombot.services import catalog_service
from ecombot.utils import compress_image

from .states import AddProduct


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
        text = manager.get_message(
            "admin_products", "add_product_categories_load_error"
        )
        if isinstance(event.message, Message):
            await event.message.edit_text(text)
            await event.answer()
        return

    if not categories:
        text = manager.get_message("admin_products", "add_product_no_categories")
        if isinstance(event.message, Message):
            await event.message.edit_text(text)
            await event.answer()
        return

    keyboard = get_catalog_categories_keyboard(categories)
    text = manager.get_message("admin_products", "add_product_choose_category")

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
            manager.get_message("admin_products", "add_product_name_prompt"),
            reply_markup=get_cancel_keyboard(),
        )
    except TelegramBadRequest as e:
        log.warning(f"Failed to edit message: {e}")
        await callback_message.answer(
            manager.get_message("admin_products", "add_product_name_prompt"),
            reply_markup=get_cancel_keyboard(),
        )
    await state.set_state(AddProduct.name)
    await query.answer()


@router.message(AddProduct.name, F.text)
async def add_product_name(message: Message, state: FSMContext):
    """Step 3: Receives the product name and asks for the description."""
    if not message.text or not message.text.strip():
        await message.answer(
            manager.get_message("admin_products", "add_product_name_empty"),
            reply_markup=get_cancel_keyboard(),
        )
        return

    product_name = message.text.strip()
    if len(product_name) > 255:
        await message.answer(
            manager.get_message("admin_products", "add_product_name_too_long"),
            reply_markup=get_cancel_keyboard(),
        )
        return

    await state.update_data(name=product_name)
    await message.answer(
        manager.get_message("admin_products", "add_product_description_prompt"),
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(AddProduct.description)


@router.message(AddProduct.description, F.text)
async def add_product_description_step(message: Message, state: FSMContext):
    """Step 4: Receives the product description and asks for the price."""
    if not message.text or not message.text.strip():
        await message.answer(
            manager.get_message("admin_products", "add_product_description_empty"),
            reply_markup=get_cancel_keyboard(),
        )
        return

    product_description = message.text.strip()
    if len(product_description) > 1000:
        await message.answer(
            manager.get_message("admin_products", "add_product_description_too_long"),
            reply_markup=get_cancel_keyboard(),
        )
        return

    await state.update_data(description=product_description)
    await message.answer(
        manager.get_message("admin_products", "add_product_price_prompt"),
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(AddProduct.price)


@router.message(AddProduct.price, F.text)
async def add_product_price_step(message: Message, state: FSMContext):
    """Step 5: Receives the price, validates it, and asks for the stock quantity."""
    try:
        price = Decimal(message.text)
        if price <= 0:
            await message.answer(
                manager.get_message("admin_products", "add_product_price_invalid"),
                reply_markup=get_cancel_keyboard(),
            )
            return
    except decimal.InvalidOperation:
        await message.answer(
            manager.get_message("admin_products", "add_product_price_format_error"),
            reply_markup=get_cancel_keyboard(),
        )
        return

    await state.update_data(price=price)
    await message.answer(
        manager.get_message("admin_products", "add_product_stock_prompt"),
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(AddProduct.stock)


@router.message(AddProduct.stock, F.text)
async def add_product_stock_step(message: Message, state: FSMContext):
    """Step 6: Receives the stock, validates it, and asks for the product image."""
    if not message.text:
        await message.answer(
            manager.get_message("admin_products", "add_product_stock_not_text")
        )
        return

    try:
        stock = int(message.text)
        if stock < 0:
            await message.answer(
                manager.get_message("admin_products", "add_product_stock_negative"),
                reply_markup=get_cancel_keyboard(),
            )
            return
    except ValueError:
        await message.answer(
            manager.get_message("admin_products", "add_product_stock_invalid"),
            reply_markup=get_cancel_keyboard(),
        )
        return

    await state.update_data(stock=stock)
    await message.answer(
        manager.get_message("admin_products", "add_product_image_prompt"),
        reply_markup=get_add_product_image_keyboard(),
    )
    await state.set_state(AddProduct.get_image)


@router.message(AddProduct.get_image, F.photo)
async def add_product_handle_photo(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Step 7a: Receives a photo, saves it, and waits for more."""
    photo: PhotoSize = message.photo[-1]
    settings.PRODUCT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    unique_filename = f"{uuid.uuid4()}.jpg"
    destination = settings.PRODUCT_IMAGE_DIR / unique_filename
    await bot.download(file=photo.file_id, destination=destination)
    image_path = str(destination)

    # Compress the image in a background thread
    await compress_image(image_path)

    data = await state.get_data()
    images = data.get("images", [])
    images.append(image_path)
    await state.update_data(images=images)

    count = len(images)
    await message.answer(
        manager.get_message(
            "admin_products", "add_product_image_saved_count", count=count
        ),
        reply_markup=get_add_product_image_keyboard(),
    )


@router.message(AddProduct.get_image, or_f(Command("done"), Command("skip")))
@router.callback_query(AddProduct.get_image, AddProductImageCallbackFactory.filter())
async def add_product_finish(
    event: Message | CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Step 7b (Final): Finishes upload and creates the product."""
    if isinstance(event, CallbackQuery):
        message = event.message
        user = event.from_user
        if message:
            await message.edit_reply_markup(reply_markup=None)
        await event.answer()
    else:
        message = event
        user = event.from_user

    product_data = await state.get_data()
    images = product_data.get("images", [])

    try:
        new_product = await catalog_service.add_new_product(
            session=session,
            name=product_data["name"],
            description=product_data["description"],
            price=product_data["price"],
            stock=product_data["stock"],
            category_id=product_data["category_id"],
            images=images,
        )
        await message.answer(
            manager.get_message(
                "admin_products", "add_product_success", name=new_product.name
            )
        )

    except Exception as e:
        # Cleanup images on failure
        for img_path in images:
            try:
                Path(img_path).unlink()
                log.info(f"Cleaned up orphaned image file: {img_path}")
            except OSError as cleanup_e:
                log.error(f"Failed to cleanup image file {img_path}: {cleanup_e}")

        admin_id: str = "Unknown"
        if user:
            admin_id = str(user.id)
        log.error(
            f"Failed to create product. Admin: {admin_id}. Error: {e}",
            exc_info=True,
        )
        await message.answer(manager.get_message("admin_products", "add_product_error"))
    finally:
        await state.clear()
