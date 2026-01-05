"""Edit product workflow handlers."""

import decimal
import uuid
from decimal import Decimal

from aiogram import Bot
from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.types import PhotoSize
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import AdminCallbackFactory
from ecombot.bot.callback_data import CatalogCallbackFactory
from ecombot.bot.callback_data import EditProductCallbackFactory
from ecombot.bot.keyboards.admin import get_admin_panel_keyboard
from ecombot.bot.keyboards.admin import get_edit_product_menu_keyboard
from ecombot.bot.keyboards.catalog import get_catalog_categories_keyboard
from ecombot.bot.keyboards.catalog import get_catalog_products_keyboard
from ecombot.bot.keyboards.common import get_cancel_keyboard
from ecombot.config import settings
from ecombot.core.manager import central_manager as manager
from ecombot.logging_setup import log
from ecombot.services import catalog_service

from ..states import EditProduct


router = Router()


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
            manager.get_message("admin_products", "edit_product_load_error"),
            reply_markup=get_admin_panel_keyboard(),
        )
        await query.answer()
        return

    if not categories:
        await callback_message.edit_text(
            manager.get_message("admin_products", "edit_product_no_categories"),
            reply_markup=get_admin_panel_keyboard(),
        )
        await query.answer()
        return

    keyboard = get_catalog_categories_keyboard(categories)
    await callback_message.edit_text(
        manager.get_message("admin_products", "edit_product_choose_category"),
        reply_markup=keyboard,
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
            reply_markup=get_admin_panel_keyboard(),
        )
        await state.clear()
        await query.answer()
        return

    if not products:
        await callback_message.edit_text(
            manager.get_message("admin_products", "edit_product_no_products"),
            reply_markup=get_admin_panel_keyboard(),
        )
        await state.clear()
        await query.answer()
        return

    keyboard = get_catalog_products_keyboard(products)
    await callback_message.edit_text(
        manager.get_message("admin_products", "edit_product_choose_product"),
        reply_markup=keyboard,
    )
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
            manager.get_message("admin_products", "edit_product_load_details_error"),
            reply_markup=get_admin_panel_keyboard(),
        )
        await state.clear()
        await query.answer()
        return

    if not product:
        await callback_message.edit_text(
            manager.get_message("admin_products", "edit_product_not_found"),
            reply_markup=get_admin_panel_keyboard(),
        )
        await state.clear()
        await query.answer()
        return

    await state.update_data(product_id=product_id, product_name=product.name)
    keyboard = get_edit_product_menu_keyboard(
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
            manager.get_message("admin_products", "edit_product_image_prompt"),
            reply_markup=get_cancel_keyboard(),
        )
        await state.update_data(edit_field="image_url")
        await state.set_state(EditProduct.get_new_image)
    else:
        field_prompts = {
            "name": manager.get_message("admin_products", "edit_product_name_prompt"),
            "description": manager.get_message(
                "admin_products", "edit_product_description_prompt"
            ),
            "price": manager.get_message("admin_products", "edit_product_price_prompt"),
            "stock": manager.get_message("admin_products", "edit_product_stock_prompt"),
        }

        await callback_message.edit_text(
            field_prompts.get(field, "Enter the new value:"),
            reply_markup=get_cancel_keyboard(),
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
            manager.get_message("admin_products", "edit_product_value_empty"),
            reply_markup=get_cancel_keyboard(),
        )
        return

    new_value = message.text.strip()

    # Validate based on field type
    try:
        if field == "price":
            new_value = Decimal(new_value)
            if new_value <= 0:
                await message.answer(
                    manager.get_message("admin_products", "edit_product_price_invalid"),
                    reply_markup=get_cancel_keyboard(),
                )
                return
        elif field == "stock":
            new_value = int(new_value)
            if new_value < 0:
                await message.answer(
                    manager.get_message(
                        "admin_products", "edit_product_stock_negative"
                    ),
                    reply_markup=get_cancel_keyboard(),
                )
                return
        elif field in ["name", "description"]:
            max_length = 255 if field == "name" else 1000
            if len(new_value) > max_length:
                await message.answer(
                    manager.get_message(
                        "admin_products",
                        "edit_product_field_too_long",
                        field=field.capitalize(),
                        max_length=max_length,
                    ),
                    reply_markup=get_cancel_keyboard(),
                )
                return
    except (ValueError, decimal.InvalidOperation):
        await message.answer(
            manager.get_message(
                "admin_products",
                "edit_product_invalid_format",
                field_type="number" if field in ["price", "stock"] else "text",
            ),
            reply_markup=get_cancel_keyboard(),
        )
        return

    # Update the product
    try:
        await catalog_service.update_product_details(
            session, product_id, {field: new_value}
        )
        await message.answer(
            manager.get_message(
                "admin_products", "edit_product_success", name=product_name, field=field
            ),
            reply_markup=get_admin_panel_keyboard(),
        )
    except Exception as e:
        log.error(f"Failed to update product {product_id}: {e}", exc_info=True)
        await message.answer(
            manager.get_message("admin_products", "edit_product_error"),
            reply_markup=get_admin_panel_keyboard(),
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
            manager.get_message(
                "admin_products", "edit_product_image_success", name=product_name
            ),
            reply_markup=get_admin_panel_keyboard(),
        )
    except Exception as e:
        log.error(f"Failed to update product image {product_id}: {e}", exc_info=True)
        await message.answer(
            manager.get_message("admin_products", "edit_product_image_error"),
            reply_markup=get_admin_panel_keyboard(),
        )

    await state.clear()
