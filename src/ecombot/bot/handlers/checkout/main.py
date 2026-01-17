"""Main checkout handler and path determination logic."""

from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import PickupSelectCallbackFactory
from ecombot.bot.keyboards.checkout import get_fast_checkout_confirmation_keyboard
from ecombot.bot.middlewares import MessageInteractionMiddleware
from ecombot.core.manager import central_manager as manager
from ecombot.db.models import User
from ecombot.services import cart_service

from .states import CheckoutFSM
from .utils import check_courier_availability
from .utils import determine_missing_info
from .utils import generate_fast_path_confirmation_text
from .utils import get_active_pickup_points
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

    # Check delivery availability
    courier_available = await check_courier_availability(session)
    is_pickup = not courier_available

    # Determine if user has enough info for Fast Path
    is_ready_for_fast_path = False

    if courier_available:
        is_ready_for_fast_path = bool(db_user.phone and default_address)
    else:
        is_ready_for_fast_path = bool(db_user.phone)

    if is_ready_for_fast_path:
        # Store mode in state for the confirmation handler
        await state.update_data(is_pickup=is_pickup)

        if not is_pickup and default_address:
            await state.update_data(default_address_id=default_address.id)
            confirmation_text = generate_fast_path_confirmation_text(
                db_user, default_address, cart, is_pickup=False
            )
            keyboard = get_fast_checkout_confirmation_keyboard()
            await callback_message.answer(confirmation_text, reply_markup=keyboard)
            await state.set_state(CheckoutFSM.confirm_fast_path)
        else:
            # Pickup Fast Path
            pickup_points = await get_active_pickup_points(session)
            if len(pickup_points) > 1:
                # Ask user to choose
                builder = InlineKeyboardBuilder()
                for pp in pickup_points:
                    builder.button(
                        text=pp.name,
                        callback_data=PickupSelectCallbackFactory(
                            pickup_point_id=pp.id
                        ),
                    )
                builder.adjust(1)
                await callback_message.answer(
                    manager.get_message("delivery", "select_pickup_point"),
                    reply_markup=builder.as_markup(),
                )
                await state.set_state(CheckoutFSM.choosing_pickup_fast)
            elif len(pickup_points) == 1:
                # Auto-select single point
                pp = pickup_points[0]
                await state.update_data(pickup_point_id=pp.id)
                confirmation_text = generate_fast_path_confirmation_text(
                    db_user, None, cart, is_pickup=True, pickup_point=pp
                )
                keyboard = get_fast_checkout_confirmation_keyboard()
                await callback_message.answer(confirmation_text, reply_markup=keyboard)
                await state.set_state(CheckoutFSM.confirm_fast_path)
            else:
                await callback_message.answer(
                    manager.get_message("delivery", "error_no_pickup_points")
                )

    else:
        # --- SLOW PATH ---
        missing_info = determine_missing_info(
            db_user, default_address, courier_available
        )
        slow_path_msg = manager.get_message(
            "checkout", "slow_path_start", missing_info=", ".join(missing_info)
        )
        await callback_message.answer(slow_path_msg)
        await state.set_state(CheckoutFSM.getting_name)
