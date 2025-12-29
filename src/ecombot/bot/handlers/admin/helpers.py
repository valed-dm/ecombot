"""Helper functions and utilities for admin handlers."""

import contextlib
import uuid
from typing import Optional

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from aiogram.types import PhotoSize

from ecombot.bot import keyboards
from ecombot.config import settings
from ecombot.logging_setup import log
from ecombot.schemas.dto import AdminProductDTO


def get_product_edit_menu_text(product: AdminProductDTO) -> str:
    """Generates the text for the product editing menu."""
    return (
        "You are editing:\n\n"
        f"<b>{product.name}</b>\n"
        f"<i>{product.description}</i>\n\n"
        f"<b>Price:</b> {settings.CURRENCY}{product.price:.2f}\n"
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
    """Displays the product edit menu by deleting and sending a new message."""
    from aiogram.types import FSInputFile

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


async def send_main_admin_panel(message: Message) -> None:
    """A helper function to generate and send the main admin panel view."""
    keyboard = keyboards.get_admin_panel_keyboard()
    text = "Welcome to the Admin Panel! Please choose an action:"
    try:
        await message.edit_text(text, reply_markup=keyboard)
    except TelegramBadRequest as e:
        log.warning(f"Failed to edit admin panel message: {e}")
        # Delete the old message and send a new one
        with contextlib.suppress(TelegramBadRequest):
            await message.delete()
        await message.answer(text, reply_markup=keyboard)


async def process_photo_upload(
    bot: Bot, photo: PhotoSize, product_id: int
) -> Optional[str]:
    """Helper function to process photo upload for product editing."""
    try:
        settings.PRODUCT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        unique_filename = f"{uuid.uuid4()}.jpg"
        destination = settings.PRODUCT_IMAGE_DIR / unique_filename
        await bot.download(file=photo.file_id, destination=destination)
        log.info(f"Successfully downloaded new photo to {destination}")
        return str(destination)
    except Exception as e:
        log.error(
            f"Failed to download photo for product {product_id}: {e}", exc_info=True
        )
        return None


async def update_product_menu(
    bot: Bot, message: Message, updated_product: AdminProductDTO, menu_message_id: int
) -> None:
    """Helper function to update the product edit menu after successful changes."""
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
            get_product_edit_menu_text(updated_product), reply_markup=updated_keyboard
        )
