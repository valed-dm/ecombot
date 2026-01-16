"""Delete product workflow handlers."""

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
from ecombot.bot.keyboards.catalog import get_catalog_products_keyboard
from ecombot.bot.keyboards.common import get_delete_confirmation_keyboard
from ecombot.core.manager import central_manager as manager
from ecombot.logging_setup import log
from ecombot.services import catalog_service

from .states import DeleteProduct


router = Router()


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
            manager.get_message(
                "admin_products", "delete_product_load_categories_error"
            ),
            reply_markup=get_admin_panel_keyboard(),
        )
        await query.answer()
        return

    if not categories:
        await callback_message.edit_text(
            manager.get_message("admin_products", "delete_product_no_categories"),
            reply_markup=get_admin_panel_keyboard(),
        )
        await query.answer()
        return

    keyboard = get_catalog_categories_keyboard(categories)
    await callback_message.edit_text(
        manager.get_message("admin_products", "delete_product_choose_category"),
        reply_markup=keyboard,
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
            manager.get_message("admin_products", "delete_product_load_products_error"),
            reply_markup=get_admin_panel_keyboard(),
        )
        await state.clear()
        await query.answer()
        return

    if not products:
        await callback_message.edit_text(
            manager.get_message("admin_products", "delete_product_no_products"),
            reply_markup=get_admin_panel_keyboard(),
        )
        await state.clear()
        await query.answer()
        return

    keyboard = get_catalog_products_keyboard(products)
    await callback_message.edit_text(
        manager.get_message("admin_products", "delete_product_choose_product"),
        reply_markup=keyboard,
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
            manager.get_message("admin_products", "delete_product_load_product_error"),
            reply_markup=get_admin_panel_keyboard(),
        )
        await state.clear()
        await query.answer()
        return

    if not product:
        await callback_message.edit_text(
            manager.get_message("admin_products", "delete_product_not_found"),
            reply_markup=get_admin_panel_keyboard(),
        )
        await state.clear()
        await query.answer()
        return

    await state.update_data(product_id=product_id, product_name=product.name)
    keyboard = get_delete_confirmation_keyboard(
        action="delete_product", item_id=product_id
    )

    text = manager.get_message("admin_products", "delete_product_confirmation").format(
        product_name=product.name,
        product_description=product.description,
        product_price=product.price,
        product_stock=product.stock,
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
            manager.get_message("admin_products", "delete_product_cancelled"),
            reply_markup=get_admin_panel_keyboard(),
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
                manager.get_message("admin_products", "delete_product_success").format(
                    product_name=product_name
                ),
                reply_markup=get_admin_panel_keyboard(),
            )
        else:
            await callback_message.edit_text(
                manager.get_message("admin_products", "delete_product_error").format(
                    product_name=product_name
                ),
                reply_markup=get_admin_panel_keyboard(),
            )
    except Exception as e:
        log.error(f"Error deleting product {product_id}: {e}", exc_info=True)
        await callback_message.edit_text(
            manager.get_message("admin_products", "delete_product_unexpected_error"),
            reply_markup=get_admin_panel_keyboard(),
        )

    await state.clear()
    await query.answer()
