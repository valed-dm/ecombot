"""Utilities for catalog handlers."""

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.types import InputMediaPhoto
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.keyboards.catalog import get_catalog_categories_keyboard
from ecombot.bot.keyboards.catalog import get_product_details_keyboard
from ecombot.core.manager import central_manager as manager
from ecombot.db import crud
from ecombot.logging_setup import log
from ecombot.schemas.dto import ProductDTO
from ecombot.services import catalog_service


async def cleanup_media_group(state: FSMContext, bot: Bot, chat_id: int):
    """Deletes the previously sent media group messages, if any."""
    data = await state.get_data()
    media_ids = data.get("media_group_ids")
    if media_ids:
        try:
            await bot.delete_messages(chat_id=chat_id, message_ids=media_ids)
        except Exception as e:
            log.warning(f"Failed to delete media group: {e}")
        await state.update_data(media_group_ids=None)


async def show_main_catalog(
    event_target: Message,
    session: AsyncSession,
    is_edit: bool = False,
    state: FSMContext = None,
):
    """
    Display the main catalog. Can either send a new message or edit an existing one.
    """
    if state and isinstance(event_target, Message):
        await cleanup_media_group(state, event_target.bot, event_target.chat.id)

    categories = await catalog_service.get_all_categories(session)
    keyboard = get_catalog_categories_keyboard(categories)
    welcome_message = manager.get_message("catalog", "welcome_message")

    if is_edit and isinstance(event_target, Message):
        await event_target.edit_text(welcome_message, reply_markup=keyboard)
    elif isinstance(event_target, Message):
        await event_target.answer(welcome_message, reply_markup=keyboard)


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
    callback_message: Message,
    bot: Bot,
    product: ProductDTO,
    state: FSMContext = None,
    session: AsyncSession = None,
):
    """Send product details with photo if available, fallback to text."""
    text = manager.get_message(
        "catalog",
        "product_details_template",
        name=product.name,
        description=product.description,
        price=product.price,
    )
    keyboard = get_product_details_keyboard(product)

    images = product.images
    if images:
        try:
            if len(images) == 1:
                img = images[0]
                # Try using cached Telegram ID first, otherwise fallback to local file
                photo_input = (
                    img.telegram_file_id
                    if img.telegram_file_id
                    else FSInputFile(path=img.file_id)
                )

                try:
                    msg = await bot.send_photo(
                        chat_id=callback_message.chat.id,
                        photo=photo_input,
                        caption=text,
                        reply_markup=keyboard,
                    )
                except TelegramBadRequest:
                    # Cache might be invalid/expired, retry with local file
                    photo_input = FSInputFile(path=img.file_id)
                    msg = await bot.send_photo(
                        chat_id=callback_message.chat.id,
                        photo=photo_input,
                        caption=text,
                        reply_markup=keyboard,
                    )

                # Update cache if we uploaded a fresh file
                if isinstance(photo_input, FSInputFile) and session:
                    new_file_id = msg.photo[-1].file_id
                    await crud.update_product_image_telegram_id(
                        session, img.id, new_file_id
                    )

                await callback_message.delete()
                return
            else:
                # Multiple images: send as media group
                media_group = []
                images_to_update = []  # Track images that need DB update

                # First attempt: Use cached IDs where available
                for i, img in enumerate(images):
                    if img.telegram_file_id:
                        media = InputMediaPhoto(media=img.telegram_file_id)
                    else:
                        media = InputMediaPhoto(media=FSInputFile(path=img.file_id))
                        images_to_update.append((i, img.id))
                    media_group.append(media)

                try:
                    msgs = await bot.send_media_group(
                        chat_id=callback_message.chat.id, media=media_group
                    )
                except TelegramBadRequest:
                    # Fallback: One of the cached IDs failed. Re-upload ALL from disk.
                    media_group = []
                    images_to_update = []
                    for i, img in enumerate(images):
                        media = InputMediaPhoto(media=FSInputFile(path=img.file_id))
                        images_to_update.append((i, img.id))
                        media_group.append(media)

                    msgs = await bot.send_media_group(
                        chat_id=callback_message.chat.id, media=media_group
                    )

                # Update DB for any images that were uploaded from disk
                if images_to_update and session:
                    for idx, img_id in images_to_update:
                        # msgs list corresponds to media_group list order
                        new_file_id = msgs[idx].photo[-1].file_id
                        await crud.update_product_image_telegram_id(
                            session, img_id, new_file_id
                        )

                if state:
                    await state.update_data(
                        media_group_ids=[m.message_id for m in msgs]
                    )

                # Send keyboard as a separate message
                await bot.send_message(
                    chat_id=callback_message.chat.id, text=text, reply_markup=keyboard
                )
                await callback_message.delete()
                return
        except Exception as e:
            log.warning(f"Failed to send images for product {product.id}: {e}")

    # Fallback to text message
    await callback_message.edit_text(text, reply_markup=keyboard)
