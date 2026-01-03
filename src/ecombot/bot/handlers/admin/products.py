"""Product management handlers."""

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
from ecombot.bot.callback_data import ConfirmationCallbackFactory
from ecombot.bot.callback_data import EditProductCallbackFactory
from ecombot.config import settings
from ecombot.logging_setup import log
from ecombot.services import catalog_service

from .states import AddProduct
from .states import DeleteProduct
from .states import EditProduct


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


@router.callback_query(AdminCallbackFactory.filter(F.action == "edit_product"))  # type: ignore[arg-type]
async def edit_product_start(
    query: CallbackQuery,
    callback_data: AdminCallbackFactory,
    session: AsyncSession,
    state: FSMContext,
    callback_message: Message,
):
    """Step 1 (Edit Product): Shows list of categories to choose from."""
    try:
        categories = await catalog_service.get_all_categories(session)
    except Exception as e:
        log.error(f"Failed to load categories for edit product: {e}", exc_info=True)
        await callback_message.edit_text(
            "❌ An unexpected error occurred while loading categories.",
            reply_markup=keyboards.get_admin_panel_keyboard(),
        )
        await query.answer()
        return

    if not categories:
        await callback_message.edit_text(
            "❌ No categories found. Please create categories and products first.",
            reply_markup=keyboards.get_admin_panel_keyboard(),
        )
        await query.answer()
        return

    keyboard = keyboards.get_catalog_categories_keyboard(categories)
    await callback_message.edit_text(
        "Choose a category to edit products from:", reply_markup=keyboard
    )
    await state.set_state(EditProduct.choose_category)
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
    """Step 2 (Edit Product): Shows products in selected category."""
    category_id = callback_data.item_id
    try:
        products = await catalog_service.get_products_in_category(session, category_id)
    except Exception as e:
        log.error(f"Failed to load products for edit: {e}", exc_info=True)
        await callback_message.edit_text(
            "❌ An unexpected error occurred while loading products.",
            reply_markup=keyboards.get_admin_panel_keyboard(),
        )
        await state.clear()
        await query.answer()
        return

    if not products:
        await callback_message.edit_text(
            "❌ No products found in this category. Please add products first.",
            reply_markup=keyboards.get_admin_panel_keyboard(),
        )
        await state.clear()
        await query.answer()
        return

    keyboard = keyboards.get_catalog_products_keyboard(products)
    await callback_message.edit_text("Choose a product to edit:", reply_markup=keyboard)
    await state.set_state(EditProduct.choose_product)
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
):
    """Step 3 (Edit Product): Shows edit menu for selected product."""
    product_id = callback_data.item_id
    try:
        product = await catalog_service.get_single_product_details_for_admin(
            session, product_id
        )
    except Exception as e:
        log.error(f"Failed to load product for edit: {e}", exc_info=True)
        await callback_message.edit_text(
            "❌ An unexpected error occurred while loading product.",
            reply_markup=keyboards.get_admin_panel_keyboard(),
        )
        await state.clear()
        await query.answer()
        return

    if not product:
        await callback_message.edit_text(
            "❌ Product not found.",
            reply_markup=keyboards.get_admin_panel_keyboard(),
        )
        await state.clear()
        await query.answer()
        return

    await state.update_data(product_id=product_id, product_name=product.name)
    keyboard = keyboards.get_edit_product_menu_keyboard(
        product_id=product_id,
        product_list_message_id=callback_message.message_id,
        category_id=product.category.id,
    )

    text = (
        f"You are editing:\n\n"
        f"<b>{product.name}</b>\n"
        f"<i>{product.description}</i>\n\n"
        f"<b>Price:</b> ${product.price:.2f}\n"
        f"<b>Stock:</b> {product.stock} units\n\n"
        "Choose a field to edit:"
    )

    await callback_message.edit_text(text, reply_markup=keyboard)
    await state.set_state(EditProduct.choose_field)
    await query.answer()


@router.callback_query(
    EditProduct.choose_field,
    EditProductCallbackFactory.filter(),  # type: ignore[arg-type]
)
async def edit_product_choose_field(
    query: CallbackQuery,
    callback_data: EditProductCallbackFactory,
    state: FSMContext,
    callback_message: Message,
):
    """Step 4 (Edit Product): Handles field selection and prompts for new value."""
    field = callback_data.action

    if field == "change_photo":
        await callback_message.edit_text(
            "Please upload a new photo for the product:",
            reply_markup=keyboards.get_cancel_keyboard(),
        )
        await state.update_data(edit_field="image_url")
        await state.set_state(EditProduct.get_new_image)
    else:
        field_prompts = {
            "name": "Enter the new product name:",
            "description": "Enter the new product description:",
            "price": "Enter the new price (e.g., 25.99):",
            "stock": "Enter the new stock quantity:",
        }

        await callback_message.edit_text(
            field_prompts.get(field, "Enter the new value:"),
            reply_markup=keyboards.get_cancel_keyboard(),
        )
        await state.update_data(edit_field=field)
        await state.set_state(EditProduct.get_new_value)

    await query.answer()


@router.message(EditProduct.get_new_value, F.text)
async def edit_product_get_new_value(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    """Step 5 (Edit Product): Processes new text value and updates product."""
    state_data = await state.get_data()
    field = state_data.get("edit_field")
    product_id = state_data.get("product_id")
    product_name = state_data.get("product_name", "the product")

    if not message.text or not message.text.strip():
        await message.answer(
            "Please enter a valid value (cannot be empty).",
            reply_markup=keyboards.get_cancel_keyboard(),
        )
        return

    new_value = message.text.strip()

    # Validate based on field type
    try:
        if field == "price":
            new_value = Decimal(new_value)
            if new_value <= 0:
                await message.answer(
                    "Price must be a positive number. Please try again.",
                    reply_markup=keyboards.get_cancel_keyboard(),
                )
                return
        elif field == "stock":
            new_value = int(new_value)
            if new_value < 0:
                await message.answer(
                    "Stock cannot be negative. Please try again.",
                    reply_markup=keyboards.get_cancel_keyboard(),
                )
                return
        elif field in ["name", "description"]:
            max_length = 255 if field == "name" else 1000
            if len(new_value) > max_length:
                await message.answer(
                    f"{field.capitalize()} is too long "
                    f"(maximum {max_length} characters).",
                    reply_markup=keyboards.get_cancel_keyboard(),
                )
                return
    except (ValueError, decimal.InvalidOperation):
        field_type = "number" if field in ["price", "stock"] else "text"
        await message.answer(
            f"Invalid {field_type} format. Please try again.",
            reply_markup=keyboards.get_cancel_keyboard(),
        )
        return

    # Update the product
    try:
        await catalog_service.update_product_details(
            session, product_id, {field: new_value}
        )
        await message.answer(
            f"✅ Product '{product_name}' {field} updated successfully!",
            reply_markup=keyboards.get_admin_panel_keyboard(),
        )
    except Exception as e:
        log.error(f"Failed to update product {product_id}: {e}", exc_info=True)
        await message.answer(
            "❌ An unexpected error occurred while updating the product.",
            reply_markup=keyboards.get_admin_panel_keyboard(),
        )

    await state.clear()


@router.message(EditProduct.get_new_image, F.photo)
async def edit_product_get_new_image(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot,
):
    """Step 5 (Edit Product): Processes new image and updates product."""
    state_data = await state.get_data()
    product_id = state_data.get("product_id")
    product_name = state_data.get("product_name", "the product")

    try:
        # Save new image
        photo: PhotoSize = message.photo[-1]
        settings.PRODUCT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        unique_filename = f"{uuid.uuid4()}.jpg"
        destination = settings.PRODUCT_IMAGE_DIR / unique_filename
        await bot.download(file=photo.file_id, destination=destination)
        image_path = str(destination)

        # Update product
        await catalog_service.update_product_details(
            session, product_id, {"image_url": image_path}
        )

        await message.answer(
            f"✅ Product '{product_name}' image updated successfully!",
            reply_markup=keyboards.get_admin_panel_keyboard(),
        )
    except Exception as e:
        log.error(f"Failed to update product image {product_id}: {e}", exc_info=True)
        await message.answer(
            "❌ An unexpected error occurred while updating the product image.",
            reply_markup=keyboards.get_admin_panel_keyboard(),
        )

    await state.clear()


@router.callback_query(AdminCallbackFactory.filter(F.action == "delete_product"))  # type: ignore[arg-type]
async def delete_product_start(
    query: CallbackQuery,
    callback_data: AdminCallbackFactory,
    session: AsyncSession,
    state: FSMContext,
    callback_message: Message,
):
    """Step 1 (Delete Product): Shows list of categories to choose from."""
    try:
        categories = await catalog_service.get_all_categories(session)
    except Exception as e:
        log.error(f"Failed to load categories for delete product: {e}", exc_info=True)
        await callback_message.edit_text(
            "❌ An unexpected error occurred while loading categories.",
            reply_markup=keyboards.get_admin_panel_keyboard(),
        )
        await query.answer()
        return

    if not categories:
        await callback_message.edit_text(
            "❌ No categories found. Please create categories and products first.",
            reply_markup=keyboards.get_admin_panel_keyboard(),
        )
        await query.answer()
        return

    keyboard = keyboards.get_catalog_categories_keyboard(categories)
    await callback_message.edit_text(
        "Choose a category to delete products from:", reply_markup=keyboard
    )
    await state.set_state(DeleteProduct.choose_category)
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
    """Step 2 (Delete Product): Shows products in selected category."""
    category_id = callback_data.item_id
    try:
        products = await catalog_service.get_products_in_category(session, category_id)
    except Exception as e:
        log.error(f"Failed to load products for delete: {e}", exc_info=True)
        await callback_message.edit_text(
            "❌ An unexpected error occurred while loading products.",
            reply_markup=keyboards.get_admin_panel_keyboard(),
        )
        await state.clear()
        await query.answer()
        return

    if not products:
        await callback_message.edit_text(
            "❌ No products found in this category.",
            reply_markup=keyboards.get_admin_panel_keyboard(),
        )
        await state.clear()
        await query.answer()
        return

    keyboard = keyboards.get_catalog_products_keyboard(products)
    await callback_message.edit_text(
        "Choose a product to delete:", reply_markup=keyboard
    )
    await state.set_state(DeleteProduct.choose_product)
    await query.answer()


@router.callback_query(
    DeleteProduct.choose_product,
    CatalogCallbackFactory.filter(F.action == "view_product"),  # type: ignore[arg-type]
)
async def delete_product_choose_product(
    query: CallbackQuery,
    callback_data: CatalogCallbackFactory,
    session: AsyncSession,
    state: FSMContext,
    callback_message: Message,
):
    """Step 3 (Delete Product): Shows confirmation for selected product."""
    product_id = callback_data.item_id
    try:
        product = await catalog_service.get_single_product_details_for_admin(
            session, product_id
        )
    except Exception as e:
        log.error(f"Failed to load product for delete: {e}", exc_info=True)
        await callback_message.edit_text(
            "❌ An unexpected error occurred while loading product.",
            reply_markup=keyboards.get_admin_panel_keyboard(),
        )
        await state.clear()
        await query.answer()
        return

    if not product:
        await callback_message.edit_text(
            "❌ Product not found.",
            reply_markup=keyboards.get_admin_panel_keyboard(),
        )
        await state.clear()
        await query.answer()
        return

    await state.update_data(product_id=product_id, product_name=product.name)
    keyboard = keyboards.get_delete_confirmation_keyboard(
        action="delete_product", item_id=product_id
    )

    text = (
        f"⚠️ Are you sure you want to permanently delete this product?\n\n"
        f"<b>{product.name}</b>\n"
        f"<i>{product.description}</i>\n\n"
        f"<b>Price:</b> ${product.price:.2f}\n"
        f"<b>Stock:</b> {product.stock} units\n\n"
        "This action cannot be undone."
    )

    await callback_message.edit_text(text, reply_markup=keyboard)
    await state.set_state(DeleteProduct.confirm_deletion)
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
    """Step 4 (Delete Product): Processes the final confirmation."""
    if not callback_data.confirm:
        await callback_message.edit_text(
            "Deletion cancelled.",
            reply_markup=keyboards.get_admin_panel_keyboard(),
        )
        await state.clear()
        await query.answer()
        return

    state_data = await state.get_data()
    product_name = state_data.get("product_name", "the product")
    product_id = callback_data.item_id

    try:
        success = await catalog_service.delete_product_by_id(session, product_id)
        if success:
            await callback_message.edit_text(
                f"✅ Product '{product_name}' has been deleted.",
                reply_markup=keyboards.get_admin_panel_keyboard(),
            )
        else:
            await callback_message.edit_text(
                f"❌ Error: Could not delete '{product_name}'. "
                f"It may have already been removed.",
                reply_markup=keyboards.get_admin_panel_keyboard(),
            )
    except Exception as e:
        log.error(f"Error deleting product {product_id}: {e}", exc_info=True)
        await callback_message.edit_text(
            "An unexpected error occurred while deleting the product.",
            reply_markup=keyboards.get_admin_panel_keyboard(),
        )

    await state.clear()
    await query.answer()
