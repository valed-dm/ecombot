"""
Admin Panel Handlers for the E-commerce Bot.

This module contains all the logic for administrative tasks, such as adding
new products and categories. It uses the Aiogram FSM (Finite State Machine)
to guide administrators through multistep processes.

All handlers in this module are protected by the `IsAdmin` filter.
"""

import decimal
import uuid
from contextlib import suppress
from decimal import Decimal
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Optional

from aiogram import Bot
from aiogram import F
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup
from aiogram.types import CallbackQuery
from aiogram.types import FSInputFile
from aiogram.types import Message
from aiogram.types import PhotoSize
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot import keyboards
from ecombot.bot.callback_data import AdminNavCallbackFactory
from ecombot.bot.callback_data import CatalogCallbackFactory
from ecombot.bot.callback_data import ConfirmationCallbackFactory
from ecombot.bot.callback_data import EditProductCallbackFactory
from ecombot.bot.filters.is_admin import IsAdmin
from ecombot.bot.middlewares import MessageInteractionMiddleware
from ecombot.config import settings
from ecombot.db.models import Category
from ecombot.logging_setup import log
from ecombot.schemas.dto import AdminProductDTO
from ecombot.services import catalog_service
from ecombot.services.catalog_service import CategoryAlreadyExistsError
from ecombot.services.catalog_service import CategoryNotEmptyError


# =============================================================================
# Router and State Definitions
# =============================================================================

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())
router.callback_query.middleware(MessageInteractionMiddleware())


class AddCategory(StatesGroup):
    name = State()
    description = State()


class AddProduct(StatesGroup):
    choose_category = State()
    name = State()
    description = State()
    price = State()
    stock = State()
    get_image = State()


class EditProduct(StatesGroup):
    choose_category = State()
    choose_product = State()
    choose_field = State()
    get_new_value = State()
    get_new_image = State()


class DeleteProduct(StatesGroup):
    choose_category = State()
    choose_product = State()
    confirm_deletion = State()


class DeleteCategory(StatesGroup):
    choose_category = State()
    confirm_deletion = State()


# =============================================================================
# Universal FSM Cancellation Handler
# =============================================================================


@router.message(Command("cancel"), StateFilter("*"))
@router.callback_query(F.data == "cancel_fsm", StateFilter("*"))
async def cancel_fsm_handler(
    event: Message | CallbackQuery,
    state: FSMContext,
):
    """
    Universal handler to cancel any active FSM state for the user,
    triggered by a /cancel command or a 'Cancel' button.
    """
    current_state = await state.get_state()
    if current_state is None:
        if isinstance(event, CallbackQuery):
            await event.answer("You are not in an active process.", show_alert=True)
        elif isinstance(event, Message):
            await event.answer("You are not in an active process.")
        return

    await state.clear()

    if isinstance(event, Message):
        await event.answer("Action cancelled. You have exited the current process.")
    elif isinstance(event, CallbackQuery) and isinstance(event.message, Message):
        try:
            await event.message.edit_text("Action cancelled.")
        except TelegramBadRequest as e:
            log.warning(f"Failed to edit cancellation message: {e}")
            await event.message.answer("Action cancelled.")
        await event.answer()


# =============================================================================
# Helper Functions
# =============================================================================


def get_product_edit_menu_text(product: AdminProductDTO) -> str:
    """
    Generates the text for the product editing menu.
    """
    return (
        "You are editing:\n\n"
        f"<b>{product.name}</b>\n"
        f"<i>{product.description}</i>\n\n"
        f"<b>Price:</b> ${product.price:.2f}\n"
        f"<b>Stock:</b> {product.stock} units\n\n"
        "Choose a field to edit:"
    )


async def send_product_edit_menu(
    bot: Bot,
    chat_id: int,
    message_to_replace: Message,
    product: AdminProductDTO,
    product_list_message_id: int,
    category_id: int,
) -> Message:
    """
    Displays the product edit menu by deleting the old message and sending a new one.
    Shows a photo if available. Returns the newly sent message object.
    """
    text = get_product_edit_menu_text(product)
    keyboard = keyboards.get_edit_product_menu_keyboard(
        product_id=product.id,
        product_list_message_id=product_list_message_id,
        category_id=category_id,
    )

    try:
        await message_to_replace.delete()
    except TelegramBadRequest as e:
        log.warning(f"Could not delete previous message in admin menu: {e}")

    new_message: Message
    if product.image_url:
        try:
            photo_file = FSInputFile(path=product.image_url)
            new_message = await bot.send_photo(
                chat_id=chat_id,
                photo=photo_file,
                caption=text,
                reply_markup=keyboard,
            )
        except (FileNotFoundError, TelegramBadRequest) as e:
            log.warning(f"Admin photo not found, sending text fallback: {e}")
            new_message = await bot.send_message(
                chat_id=chat_id, text=text, reply_markup=keyboard
            )
    else:
        new_message = await bot.send_message(
            chat_id=chat_id, text=text, reply_markup=keyboard
        )

    return new_message


async def send_main_admin_panel(message: Message):
    """
    A helper function to generate and send the main admin panel view.
    Attempts to edit the message, falling back to sending a new one.
    """
    keyboard = keyboards.get_admin_panel_keyboard()
    text = "Welcome to the Admin Panel! Please choose an action:"
    try:
        await message.edit_text(text, reply_markup=keyboard)
    except TelegramBadRequest as e:
        log.warning(f"Failed to edit admin panel message: {e}")
        try:
            await message.answer(text, reply_markup=keyboard)
        except Exception as fallback_e:
            log.error(f"Failed to send fallback admin panel message: {fallback_e}")
            raise


# =============================================================================
# Main Admin Panel Entry Point
# =============================================================================


@router.message(Command("admin"))
async def command_admin_panel(message: Message):
    """
    Handler for the /admin command. Displays the main admin actions keyboard.
    """
    await send_main_admin_panel(message)


# =============================================================================
# "Add Category" FSM Handlers
# =============================================================================


@router.callback_query(F.data == "admin:add_category")
async def add_category_start(
    query: CallbackQuery,
    state: FSMContext,
    callback_message: Message,
):
    """
    Step 1: Starts the "Add Category" FSM. Asks for the category name.
    """
    await callback_message.edit_text(
        "Please enter the name for the new category:",
        reply_markup=keyboards.get_cancel_keyboard(),
    )
    await state.set_state(AddCategory.name)
    await query.answer()


@router.message(AddCategory.name, F.text)
async def add_category_name(message: Message, state: FSMContext):
    """
    Step 2: Receives the category name and asks for the description.
    """
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
    """
    Step 3: Receives the description (or /skip) and creates the category.
    This is the final step of the "Add Category" FSM.
    """
    category_data = await state.get_data()
    description = message.text if message.text != "/skip" else None

    try:
        new_category = await catalog_service.add_new_category(
            session=session, name=category_data["name"], description=description
        )
        await message.answer(f"✅ Category '{new_category.name}' created successfully!")
    except CategoryAlreadyExistsError as e:
        await message.answer(f"⚠️ Error: {e}")
    except Exception as e:
        log.error(f"Failed to create category: {e}", exc_info=True)
        await message.answer("❌ An unexpected error occurred while creating the category.")
    finally:
        await state.clear()


# =============================================================================
# "Add Product" FSM Handlers
# =============================================================================


@router.message(Command("add_product"))
@router.callback_query(F.data == "admin:add_product")
async def add_product_start(
    event: Message | CallbackQuery, session: AsyncSession, state: FSMContext
):
    """
    Step 1: Starts the "Add Product" FSM. Asks the admin to choose a category.
    """
    categories = await catalog_service.get_all_categories(session)
    
    if not categories:
        text = (
            "❌ No categories found. You need to create at least one category "
            "before adding products. Please use 'Add Category' first."
        )
        if isinstance(event, Message):
            await event.answer(text)
        elif isinstance(event, CallbackQuery) and isinstance(event.message, Message):
            await event.message.edit_text(text)
            await event.answer()
        return
    
    keyboard = keyboards.get_catalog_categories_keyboard(categories)
    text = "Please choose the category for the new product:"

    if isinstance(event, Message):
        await event.answer(text, reply_markup=keyboard)
    elif isinstance(event, CallbackQuery) and isinstance(event.message, Message):
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
    """
    Step 2: Receives the category and asks for the product name.
    """
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
    """
    Step 3: Receives the product name and asks for the description.
    """
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
    """
    Step 4: Receives the product description and asks for the price.
    """
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
    """
    Step 5: Receives the price, validates it, and asks for the stock quantity.
    """
    try:
        price = Decimal(message.text)
        if price <= 0:
            await message.answer("Price must be a positive number. Please try again.")
            return
    except decimal.InvalidOperation:
        await message.answer(
            "Invalid price format. Please enter a number (e.g., 25.99)."
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
    """
    Step 6: Receives the stock, validates it, and asks for the product image.
    """
    if not message.text:
        await message.answer("Please send the stock quantity as text, not a photo or sticker.")
        return

    try:
        stock = int(message.text)
        if stock < 0:
            await message.answer(
                "Stock cannot be negative. Please enter a whole number."
            )
            return
    except ValueError:
        await message.answer("Invalid format. Please enter a whole number.")
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
    """
    Step 7 (Final): Receives the photo (or /skip), saves it, and creates the product.
    """
    image_path: Optional[str] = None
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
            f"Failed to create product. Admin: {admin_id}." f" Error: {e}",
            exc_info=True,
        )
        await message.answer(
            "❌ An unexpected error occurred while creating the product. "
            "Please check the logs for details."
        )
    finally:
        await state.clear()


# =============================================================================
# "Edit Product" FSM Handlers
# =============================================================================


@router.callback_query(F.data == "admin:edit_product")
async def edit_product_start(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    callback_message: Message,
):
    """Step 1: Starts the "Edit Product" FSM. Asks for a category."""
    try:
        categories = await catalog_service.get_all_categories(session)
        keyboard = keyboards.get_catalog_categories_keyboard(categories)
        await callback_message.edit_text(
            "Please choose a category to find the product you want to edit:",
            reply_markup=keyboard,
        )
        await state.set_state(EditProduct.choose_category)
        await query.answer()
    except Exception as e:
        log.error(f"Failed to load categories for edit product: {e}", exc_info=True)
        await callback_message.edit_text("❌ An unexpected error occurred while loading categories.")
        await state.clear()
        await query.answer()


@router.callback_query(
    EditProduct.choose_category,
    CatalogCallbackFactory.filter(F.action == "view_category"),  # type: ignore[arg-type]
)
async def edit_product_choose_category(
    query: CallbackQuery,
    callback_data: CatalogCallbackFactory,
    session: AsyncSession,
    state: FSMContext,
    callback_message: Message,
):
    """Step 2: Receives the category, asks for a product."""
    category_id = callback_data.item_id
    await state.update_data(category_id=category_id)
    try:
        products = await catalog_service.get_products_in_category(session, category_id)
        keyboard = keyboards.get_catalog_products_keyboard(products)
        await callback_message.edit_text(
            "Please choose the product you want to edit:", reply_markup=keyboard
        )
        await state.set_state(EditProduct.choose_product)
        await query.answer()
    except Exception as e:
        log.error(f"Failed to load products for category {category_id}: {e}", exc_info=True)
        await callback_message.edit_text("❌ An unexpected error occurred while loading products.")
        await state.clear()
        await query.answer()


@router.callback_query(
    EditProduct.choose_product,
    CatalogCallbackFactory.filter(F.action == "view_product"),  # type: ignore[arg-type]
)
async def edit_product_choose_product(
    query: CallbackQuery,
    callback_data: CatalogCallbackFactory,
    session: AsyncSession,
    state: FSMContext,
    callback_message: Message,
    bot: Bot,
):
    """
    Step 3: Receives the product, shows the edit menu using the 'delete and resend'
    pattern, and saves the NEW menu's message ID to the state.
    """
    product_id = callback_data.item_id

    await state.update_data(product_id=product_id)

    product = await catalog_service.get_single_product_details_for_admin(
        session, product_id
    )

    if not product:
        await query.answer("Error: Product not found.", show_alert=True)
        await state.clear()
        return

    product_list_message_id = callback_message.message_id
    await state.update_data(category_id=product.category.id)

    try:
        new_menu_message = await send_product_edit_menu(
            bot=bot,
            chat_id=callback_message.chat.id,
            message_to_replace=callback_message,
            product=product,
            product_list_message_id=product_list_message_id,
            category_id=product.category.id,
        )

        await state.update_data(menu_message_id=new_menu_message.message_id)
        await state.set_state(EditProduct.choose_field)
        await query.answer()
    except Exception as e:
        log.error(f"Failed to send product edit menu: {e}", exc_info=True)
        await callback_message.answer("❌ An unexpected error occurred while loading the edit menu.")
        await state.clear()
        await query.answer()


@router.callback_query(
    EditProduct.choose_field,
    EditProductCallbackFactory.filter(
        F.action.in_({"name", "description", "price", "stock"})
    ),
)
async def edit_product_choose_field_text(
    query: CallbackQuery,
    callback_data: EditProductCallbackFactory,
    state: FSMContext,
    callback_message: Message,
    bot: Bot,
):
    """Step 4 (Text): Asks for the new value by deleting and resending."""
    field_to_edit = callback_data.action
    product_id = callback_data.product_id

    await state.update_data(field_to_edit=field_to_edit, product_id=product_id)

    prompt_text = f"Please enter the new {field_to_edit.replace('_', ' ')}:"

    with suppress(TelegramBadRequest):
        await callback_message.delete()

    try:
        new_prompt_message = await bot.send_message(
            chat_id=callback_message.chat.id,
            text=prompt_text,
            reply_markup=keyboards.get_cancel_keyboard(),
        )

        await state.update_data(menu_message_id=new_prompt_message.message_id)
        await state.set_state(EditProduct.get_new_value)
        await query.answer()
    except TelegramBadRequest as e:
        log.error(f"Failed to send prompt message: {e}", exc_info=True)
        await callback_message.answer("❌ Failed to send prompt message. Please try again.")
        await state.clear()
        await query.answer()


@router.message(EditProduct.get_new_value, F.text)
async def edit_product_get_new_value(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot,
):
    """
    Step 5: Receives the new value, validates it, updates the product,
    and returns to the edit menu.
    """
    if not message.text:
        await message.answer("Please send data as text, not a photo or sticker.")
        return

    new_value: str = message.text
    state_data = await state.get_data()
    product_id: int = state_data["product_id"]
    field_to_edit: str = state_data["field_to_edit"]
    menu_message_id: int = state_data["menu_message_id"]

    update_data: Dict[str, Any] = {}
    try:
        if field_to_edit == "price":
            parsed_price = Decimal(new_value)
            if parsed_price <= 0:
                await message.answer(
                    "Price must be a positive number. Please try again.",
                    reply_markup=keyboards.get_cancel_keyboard(),
                )
                return
            update_data["price"] = parsed_price

        elif field_to_edit == "stock":
            parsed_stock = int(new_value)
            if parsed_stock < 0:
                await message.answer(
                    "Stock cannot be negative. Please try again.",
                    reply_markup=keyboards.get_cancel_keyboard(),
                )
                return
            update_data["stock"] = parsed_stock

        elif field_to_edit in ["name", "description"]:
            update_data[field_to_edit] = new_value

        else:
            await message.answer(
                "An internal error occurred (unknown field). Cancelling."
            )
            await state.clear()
            return

    except (ValueError, decimal.InvalidOperation):
        await message.answer(
            f"Invalid format for {field_to_edit}. Please enter a valid number.",
            reply_markup=keyboards.get_cancel_keyboard(),
        )
        return

    try:
        updated_product = await catalog_service.update_product_details(
            session=session,
            product_id=product_id,
            update_data=update_data,
        )
        # 1. Send a temporary success confirmation
        await message.answer(f"✅ Successfully updated {field_to_edit}!")

        category_id = updated_product.category.id

        updated_keyboard = keyboards.get_edit_product_menu_keyboard(
            product_id=updated_product.id,
            product_list_message_id=menu_message_id,
            category_id=category_id,
        )

        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=menu_message_id,
            text=get_product_edit_menu_text(updated_product),
            reply_markup=updated_keyboard,
        )

        await state.set_state(EditProduct.choose_field)

    except Exception as e:
        log.error(f"Failed to update product {product_id}: {e}", exc_info=True)
        await message.answer("❌ An unexpected error occurred. Please check the logs.")
        await state.clear()


@router.callback_query(
    EditProduct.choose_field,
    EditProductCallbackFactory.filter(F.action == "change_photo"),  # type: ignore[arg-type]
)
async def edit_product_change_photo_start(
    query: CallbackQuery,
    callback_data: EditProductCallbackFactory,
    state: FSMContext,
    callback_message: Message,
):
    """
    Step 4a (Edit Photo): Asks the admin for the new photo.
    """
    await state.update_data(product_id=callback_data.product_id)
    await callback_message.edit_text(
        "Please upload the new photo for the product.\n\n"
        "You can also send /remove to delete the current photo entirely.",
        reply_markup=keyboards.get_cancel_keyboard(),
    )
    await state.set_state(EditProduct.get_new_image)
    await query.answer()


async def _process_photo_upload(bot: Bot, photo: PhotoSize, product_id: int) -> str | None:
    """
    Helper function to process photo upload for product editing.
    Returns the path to the saved image or None if processing fails.
    """
    try:
        settings.PRODUCT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        unique_filename = f"{uuid.uuid4()}.jpg"
        destination = settings.PRODUCT_IMAGE_DIR / unique_filename
        await bot.download(file=photo.file_id, destination=destination)
        log.info(f"Successfully downloaded new photo to {destination}")
        return str(destination)
    except Exception as e:
        log.error(f"Failed to download photo for product {product_id}: {e}", exc_info=True)
        return None


async def _update_product_menu(bot: Bot, message: Message, updated_product: AdminProductDTO, menu_message_id: int) -> None:
    """
    Helper function to update the product edit menu after successful changes.
    """
    updated_keyboard = keyboards.get_edit_product_menu_keyboard(
        product_id=updated_product.id,
        product_list_message_id=menu_message_id,
        category_id=updated_product.category.id,
    )
    try:
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=menu_message_id,
            text=get_product_edit_menu_text(updated_product),
            reply_markup=updated_keyboard,
        )
    except TelegramBadRequest as e:
        log.warning(f"Failed to edit message {menu_message_id}: {e}")
        await message.answer(
            get_product_edit_menu_text(updated_product),
            reply_markup=updated_keyboard
        )


@router.message(EditProduct.get_new_image, or_f(F.photo, Command("remove")))
async def edit_product_get_new_photo(
    message: Message, state: FSMContext, session: AsyncSession, bot: Bot
):
    """
    Step 5a (Edit Photo): Receives the new photo, updates the product,
    and returns to the edit menu.
    """
    state_data = await state.get_data()
    product_id = state_data["product_id"]
    menu_message_id = state_data["menu_message_id"]

    product_to_update = await catalog_service.get_single_product_details_for_admin(
        session, product_id
    )
    if not product_to_update:
        await message.answer("Error: Product not found. Cancelling operation.")
        await state.clear()
        return

    old_image_path = product_to_update.image_url
    new_image_path: str | None = None

    if message.photo:
        new_image_path = await _process_photo_upload(bot, message.photo[-1], product_id)
        if not new_image_path:
            await message.answer(
                "❌ Sorry, there was an error downloading the photo."
                " Please try a different image or check the logs."
            )
            return

    try:
        updated_product = await catalog_service.update_product_details(
            session=session,
            product_id=product_id,
            update_data={"image_url": new_image_path},
        )
        if not updated_product:
            await message.answer("Could not update the product. Please try again.")
            await state.clear()
            return

        if old_image_path and new_image_path != old_image_path:
            try:
                Path(old_image_path).unlink()
                log.info(f"Deleted old image file: {old_image_path}")
            except OSError as e:
                log.error(f"Error deleting old image file {old_image_path}: {e}")

        await message.answer("✅ Product photo updated successfully!")
        await _update_product_menu(bot, message, updated_product, menu_message_id)
        await state.set_state(EditProduct.choose_field)

    except Exception as e:
        log.error(f"Failed to process new photo for product {product_id}: {e}", exc_info=True)
        await message.answer("❌ An unexpected error occurred. Please check the logs.")
        await state.clear()


@router.callback_query(
    AdminNavCallbackFactory.filter(F.action == "back_to_product_list")  # type: ignore[arg-type]
)
async def smart_back_to_products_handler(
    query: CallbackQuery,
    callback_data: AdminNavCallbackFactory,
    session: AsyncSession,
    state: FSMContext,
    callback_message: Message,
    bot: Bot,
):
    """
    A "smart" back handler that uses state from the callback data
    to edit a specific target message, providing robust navigation.
    """
    target_message_id = callback_data.target_message_id
    category_id = callback_data.category_id

    try:
        products = await catalog_service.get_products_in_category(session, category_id)
        keyboard = keyboards.get_catalog_products_keyboard(products)
        text = "Please choose the product you want to edit:"

        try:
            await bot.edit_message_text(
                chat_id=callback_message.chat.id,
                message_id=target_message_id,
                text=text,
                reply_markup=keyboard,
            )

        except TelegramBadRequest:
            await callback_message.answer(text, reply_markup=keyboard)

        await state.set_state(EditProduct.choose_product)
        await query.answer()
    except Exception as e:
        log.error(f"Failed to load products for back navigation: {e}", exc_info=True)
        await callback_message.answer("❌ An unexpected error occurred while loading products.")
        await state.clear()
        await query.answer()


# =============================================================================
# "Delete Product" FSM Handlers
# =============================================================================


@router.callback_query(F.data == "admin:delete_product")
async def delete_product_start(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    callback_message: Message,
):
    """Step 1 (Delete): Starts FSM. Asks for a category."""
    try:
        categories = await catalog_service.get_all_categories(session)
        keyboard = keyboards.get_catalog_categories_keyboard(categories)
        await callback_message.edit_text(
            "Choose a category to find the product to delete:", reply_markup=keyboard
        )
        await state.set_state(DeleteProduct.choose_category)
        await query.answer()
    except Exception as e:
        log.error(f"Failed to load categories for delete product: {e}", exc_info=True)
        await callback_message.edit_text("❌ An unexpected error occurred while loading categories.")
        await state.clear()
        await query.answer()


@router.callback_query(
    DeleteProduct.choose_category,
    CatalogCallbackFactory.filter(F.action == "view_category"),  # type: ignore[arg-type]
)
async def delete_product_choose_category(
    query: CallbackQuery,
    callback_data: CatalogCallbackFactory,
    session: AsyncSession,
    state: FSMContext,
    callback_message: Message,
):
    """Step 2 (Delete): Receives category, asks for a product."""
    try:
        products = await catalog_service.get_products_in_category(
            session, callback_data.item_id
        )
        keyboard = keyboards.get_catalog_products_keyboard(products)
        await callback_message.edit_text(
            "Choose the product you want to delete:", reply_markup=keyboard
        )
        await state.set_state(DeleteProduct.choose_product)
        await query.answer()
    except Exception as e:
        log.error(f"Failed to load products for delete: {e}", exc_info=True)
        await callback_message.edit_text("❌ An unexpected error occurred while loading products.")
        await state.clear()
        await query.answer()


@router.callback_query(
    DeleteProduct.choose_product,
    CatalogCallbackFactory.filter(F.action == "view_product"),  # type: ignore[arg-type]
)
async def delete_product_confirm(
    query: CallbackQuery,
    callback_data: CatalogCallbackFactory,
    session: AsyncSession,
    state: FSMContext,
    callback_message: Message,
):
    """Step 3 (Delete): Receives product, asks for confirmation."""
    product_id = callback_data.item_id
    try:
        product = await catalog_service.get_single_product_details(session, product_id)
        if not product:
            await callback_message.edit_text("Error: Product not found.")
            await state.clear()
            return

        await state.update_data(product_id=product_id, product_name=product.name)
        keyboard = keyboards.get_delete_confirmation_keyboard(
            action="delete_product", item_id=product_id
        )
        await callback_message.edit_text(
            f"⚠️ Are you sure you want to permanently delete '{product.name}'?",
            reply_markup=keyboard,
        )
        await state.set_state(DeleteProduct.confirm_deletion)
        await query.answer()
    except Exception as e:
        log.error(f"Failed to load product details for deletion: {e}", exc_info=True)
        await callback_message.edit_text("❌ An unexpected error occurred while loading product details.")
        await state.clear()
        await query.answer()


@router.callback_query(
    DeleteProduct.confirm_deletion,
    ConfirmationCallbackFactory.filter(F.action == "delete_product"),  # type: ignore[arg-type]
)
async def delete_product_final(
    query: CallbackQuery,
    callback_data: ConfirmationCallbackFactory,
    session: AsyncSession,
    state: FSMContext,
    callback_message: Message,
):
    """Step 4 (Delete): Processes the final confirmation."""
    if not callback_data.confirm:
        await callback_message.edit_text("Deletion cancelled.")
        await state.clear()
        await query.answer()
        return

    state_data = await state.get_data()
    product_name = state_data.get("product_name", "the product")

    try:
        success = await catalog_service.delete_product_by_id(session, callback_data.item_id)
        if success:
            await callback_message.edit_text(
                f"✅ Product '{product_name}' has been deleted."
            )
        else:
            await callback_message.edit_text(
                f"❌ Error: Could not delete '{product_name}'."
                f" It may have already been removed."
            )
    except Exception as e:
        log.error(f"Error deleting product {callback_data.item_id}: {e}", exc_info=True)
        await callback_message.edit_text("❌ An unexpected error occurred while deleting the product.")

    await state.clear()
    await query.answer()


# =============================================================================
# "Delete Category" FSM Handlers
# =============================================================================


@router.callback_query(F.data == "admin:delete_category")
async def delete_category_start(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    callback_message: Message,
):
    """Step 1 (Delete Cat): Starts FSM. Asks for a category."""
    try:
        categories = await catalog_service.get_all_categories(session)
        keyboard = keyboards.get_catalog_categories_keyboard(categories)
        await callback_message.edit_text(
            "Choose the category you want to delete:", reply_markup=keyboard
        )
        await state.set_state(DeleteCategory.choose_category)
        await query.answer()
    except Exception as e:
        log.error(f"Failed to load categories for delete: {e}", exc_info=True)
        await callback_message.edit_text("❌ An unexpected error occurred while loading categories.")
        await state.clear()
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
    category = await session.get(
        Category, category_id
    )  # Using session.get for a quick fetch
    if not category:
        await callback_message.edit_text("Error: Category not found.")
        await state.clear()
        return

    await state.update_data(category_id=category_id, category_name=category.name)
    keyboard = keyboards.get_delete_confirmation_keyboard(
        action="delete_category", item_id=category_id
    )
    await callback_message.edit_text(
        f"⚠️ Are you sure you want to permanently delete"
        f" the category '{category.name}'?",
        reply_markup=keyboard,
    )
    await state.set_state(DeleteCategory.confirm_deletion)
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
        await callback_message.edit_text("Deletion cancelled.")
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
                f"✅ Category '{category_name}' has been deleted."
            )
        else:
            await callback_message.edit_text(
                f"❌ Error: Could not delete '{category_name}'."
                f" It may have already been removed."
            )
    except CategoryNotEmptyError:
        await callback_message.edit_text(
            f"❌ Cannot delete '{category_name}' because it still"
            f" contains products. Please move or delete them first."
        )
    except Exception as e:
        log.error(
            f"Error deleting category {callback_data.item_id}: {e}", exc_info=True
        )
        await callback_message.edit_text("An unexpected error occurred.")

    await state.clear()
    await query.answer()
