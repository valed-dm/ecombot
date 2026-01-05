"""Main checkout handler and path determination logic."""

from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.keyboards.checkout import get_fast_checkout_confirmation_keyboard
from ecombot.bot.middlewares import MessageInteractionMiddleware
from ecombot.core import manager
from ecombot.db.models import User
from ecombot.services import cart_service

from .states import CheckoutFSM
from .utils import determine_missing_info
from .utils import generate_fast_path_confirmation_text
from .utils import get_default_address


router = Router()
router.callback_query.middleware(MessageInteractionMiddleware())


@router.callback_query(F.data == "checkout_start")
async def checkout_start_handler(
    query: CallbackQuery,
    session: AsyncSession,
    db_user: User,
    state: FSMContext,
    callback_message: Message,
):
    """
    Starts the checkout process. Determines if the user can use the "fast path".
    """
    await query.answer()

    cart = await cart_service.get_user_cart(session, db_user.telegram_id)
    if not cart.items:
        error_msg = manager.get_message("checkout", "error_empty_cart")
        await callback_message.answer(error_msg)
        return

    default_address = get_default_address(db_user)

    if db_user.phone and default_address:
        # --- FAST PATH ---
        await state.update_data(default_address_id=default_address.id)
        confirmation_text = generate_fast_path_confirmation_text(
            db_user, default_address, cart
        )
        keyboard = get_fast_checkout_confirmation_keyboard()
        await callback_message.answer(confirmation_text, reply_markup=keyboard)
        await state.set_state(CheckoutFSM.confirm_fast_path)
    else:
        # --- SLOW PATH ---
        missing_info = determine_missing_info(db_user, default_address)
        slow_path_msg = manager.get_message(
            "checkout", "slow_path_start", missing_info=", ".join(missing_info)
        )
        await callback_message.answer(slow_path_msg)
        await state.set_state(CheckoutFSM.getting_name)
