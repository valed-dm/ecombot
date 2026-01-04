"""Utilities for catalog handlers."""

from aiogram import Bot
from aiogram.types import FSInputFile
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot import keyboards
from ecombot.logging_setup import log
from ecombot.schemas.dto import ProductDTO
from ecombot.services import catalog_service

from .constants import PRODUCT_DETAILS_TEMPLATE
from .constants import WELCOME_MESSAGE


async def show_main_catalog(
    event_target: Message, session: AsyncSession, is_edit: bool = False
):
    """
    Display the main catalog. Can either send a new message or edit an existing one.
    """
    categories = await catalog_service.get_all_categories(session)
    keyboard = keyboards.get_catalog_categories_keyboard(categories)

    if is_edit and isinstance(event_target, Message):
        await event_target.edit_text(WELCOME_MESSAGE, reply_markup=keyboard)
    elif isinstance(event_target, Message):
        await event_target.answer(WELCOME_MESSAGE, reply_markup=keyboard)


async def handle_message_with_photo_transition(
    callback_message: Message, bot: Bot, text: str, keyboard
):
    """Handle transition from photo message to text message or vice versa."""
    if callback_message.photo:
        await callback_message.delete()
        await bot.send_message(
            chat_id=callback_message.chat.id, text=text, reply_markup=keyboard
        )
    else:
        await callback_message.edit_text(text, reply_markup=keyboard)


async def send_product_with_photo(
    callback_message: Message, bot: Bot, product: ProductDTO
):
    """Send product details with photo if available, fallback to text."""
    text = PRODUCT_DETAILS_TEMPLATE.format(
        name=product.name, description=product.description, price=product.price
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
            return
        except Exception as e:
            log.warning(f"Failed to send image for product {product.id}: {e}")

    # Fallback to text message
    await callback_message.edit_text(text, reply_markup=keyboard)
