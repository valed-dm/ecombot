"""
Handlers for the product catalog.

This module contains handlers for navigating categories and viewing products.
"""

from aiogram import Bot
from aiogram import F
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery
from aiogram.types import FSInputFile
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot import keyboards
from ecombot.bot.callback_data import CatalogCallbackFactory
from ecombot.bot.middlewares import MessageInteractionMiddleware
from ecombot.logging_setup import log
from ecombot.services import catalog_service


router = Router()
router.callback_query.middleware(MessageInteractionMiddleware())


async def show_main_catalog(
    event_target: Message, session: AsyncSession, is_edit: bool = False
):
    """
    A helper function to display the main catalog. Can either send a new
    message or edit an existing one.
    """
    categories = await catalog_service.get_all_categories(session)
    keyboard = keyboards.get_catalog_categories_keyboard(categories)
    text = "Welcome to our store! Please choose a category to start browsing:"

    if is_edit and isinstance(event_target, Message):
        await event_target.edit_text(text, reply_markup=keyboard)
    elif isinstance(event_target, Message):
        await event_target.answer(text, reply_markup=keyboard)


@router.message(CommandStart())
async def command_start_handler(message: Message, session: AsyncSession):
    """
    Handler for the /start command. Displays the main product categories.
    """
    await show_main_catalog(message, session)


@router.callback_query(CatalogCallbackFactory.filter(F.action == "back_to_main"))  # type: ignore[arg-type]
async def back_to_main_handler(
    query: CallbackQuery,
    session: AsyncSession,
    callback_message: Message,
):
    """
    Handler for the "Back to Categories" button.
    Edits the current message to show the main catalog again.
    """
    await show_main_catalog(callback_message, session, is_edit=True)
    await query.answer()


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
    keyboard = keyboards.get_catalog_products_keyboard(products)
    text = "Here are the products in this category:"

    if callback_message.photo:
        await callback_message.delete()
        await bot.send_message(
            chat_id=callback_message.chat.id, text=text, reply_markup=keyboard
        )
    else:
        await callback_message.edit_text(text, reply_markup=keyboard)

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
        await query.answer(
            "Sorry, this product could not be found.",
            show_alert=True,
        )
        return

    text = (
        f"<b>{product.name}</b>\n\n"
        f"{product.description}\n\n"
        f"<b>Price:</b> ${product.price:.2f}"
    )
    keyboard = keyboards.get_product_details_keyboard(product)

    if product.image_url:
        try:
            photo_file = FSInputFile(path=product.image_url)

            await bot.send_photo(
                chat_id=callback_message.chat.id,
                photo=photo_file,
                caption=text,
                reply_markup=keyboard,
            )
            await callback_message.delete()

        except Exception as e:
            log.warning(f"Failed to send image for product {product.id}: {e}")
            await callback_message.edit_text(text, reply_markup=keyboard)
    else:
        await callback_message.edit_text(text, reply_markup=keyboard)

    await query.answer()
