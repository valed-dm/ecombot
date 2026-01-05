"""Category and product viewing handlers."""

from aiogram import Bot
from aiogram import F
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import CatalogCallbackFactory
from ecombot.bot.keyboards.catalog import get_catalog_products_keyboard
from ecombot.core.manager import central_manager as manager
from ecombot.services import catalog_service

from .utils import handle_message_with_photo_transition
from .utils import send_product_with_photo


router = Router()


@router.callback_query(CatalogCallbackFactory.filter(F.action == "view_category"))  # type: ignore[arg-type]
async def view_category_handler(
    query: CallbackQuery,
    callback_data: CatalogCallbackFactory,
    session: AsyncSession,
    callback_message: Message,
    bot: Bot,
):
    """
    Handler for when a user clicks on a category button OR the
    "Back to Products" button.
    """
    category_id = callback_data.item_id
    products = await catalog_service.get_products_in_category(session, category_id)
    keyboard = get_catalog_products_keyboard(products)

    category_products_message = manager.get_message(
        "catalog", "category_products_message"
    )
    await handle_message_with_photo_transition(
        callback_message, bot, category_products_message, keyboard
    )
    await query.answer()


@router.callback_query(CatalogCallbackFactory.filter(F.action == "view_product"))  # type: ignore[arg-type]
async def view_product_handler(
    query: CallbackQuery,
    callback_data: CatalogCallbackFactory,
    session: AsyncSession,
    callback_message: Message,
    bot: Bot,
):
    """
    Handler for when a user clicks on a specific product.
    Displays the product details, including a photo if available.
    """
    product_id = callback_data.item_id
    product = await catalog_service.get_single_product_details(session, product_id)

    if not product:
        error_message = manager.get_message("catalog", "error_product_not_found")
        await query.answer(error_message, show_alert=True)
        return

    await send_product_with_photo(callback_message, bot, product)
    await query.answer()
