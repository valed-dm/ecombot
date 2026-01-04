"""Category and product viewing handlers."""

from aiogram import Bot
from aiogram import F
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import CatalogCallbackFactory
from ecombot.bot.keyboards.catalog import get_catalog_products_keyboard
from ecombot.services import catalog_service

from .constants import CATEGORY_PRODUCTS_MESSAGE
from .constants import ERROR_PRODUCT_NOT_FOUND
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

    await handle_message_with_photo_transition(
        callback_message, bot, CATEGORY_PRODUCTS_MESSAGE, keyboard
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
        await query.answer(ERROR_PRODUCT_NOT_FOUND, show_alert=True)
        return

    await send_product_with_photo(callback_message, bot, product)
    await query.answer()
