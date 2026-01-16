"""Fast path checkout handlers for returning users."""

from html import escape

from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import CheckoutCallbackFactory
from ecombot.bot.callback_data import PickupSelectCallbackFactory
from ecombot.bot.keyboards.checkout import get_fast_checkout_confirmation_keyboard
from ecombot.bot.middlewares import MessageInteractionMiddleware
from ecombot.core.manager import central_manager as manager
from ecombot.db.models import DeliveryAddress
from ecombot.db.models import PickupPoint
from ecombot.db.models import User
from ecombot.logging_setup import logger
from ecombot.schemas.dto import OrderDTO
from ecombot.schemas.enums import DeliveryType
from ecombot.services import cart_service
from ecombot.services import notification_service
from ecombot.services import order_service
from ecombot.services.order_service import OrderPlacementError

from .states import CheckoutFSM
from .utils import generate_fast_path_confirmation_text


router = Router()
router.callback_query.middleware(MessageInteractionMiddleware())


@router.callback_query(
    CheckoutFSM.choosing_pickup_fast, PickupSelectCallbackFactory.filter()
)
async def fast_path_pickup_selected(
    query: CallbackQuery,
    callback_data: PickupSelectCallbackFactory,
    state: FSMContext,
    session: AsyncSession,
    db_user: User,
):
    """Handles pickup point selection in fast path."""
    pp_id = callback_data.pickup_point_id
    pickup_point = await session.get(PickupPoint, pp_id)
    if not pickup_point:
        await query.answer("Invalid pickup point.", show_alert=True)
        return

    await state.update_data(pickup_point_id=pp_id)

    # Generate confirmation
    cart = await cart_service.get_user_cart(session, db_user.telegram_id)
    confirmation_text = generate_fast_path_confirmation_text(
        db_user,
        None,
        cart,
        is_pickup=True,
        pickup_point=pickup_point,
    )
    keyboard = get_fast_checkout_confirmation_keyboard()

    await query.message.edit_text(confirmation_text, reply_markup=keyboard)
    await state.set_state(CheckoutFSM.confirm_fast_path)


@router.callback_query(
    CheckoutFSM.confirm_fast_path,
    CheckoutCallbackFactory.filter(F.action == "confirm"),  # type: ignore[arg-type]
)
async def fast_checkout_confirm_handler(
    query: CallbackQuery,
    session: AsyncSession,
    db_user: User,
    state: FSMContext,
    callback_message: Message,
):
    """Handles the final confirmation for the fast path checkout."""
    progress_msg = manager.get_message("checkout", "progress_placing_order")
    await callback_message.edit_text(progress_msg)

    state_data = await state.get_data()
    default_address_id = state_data.get("default_address_id")
    is_pickup = state_data.get("is_pickup", False)
    pickup_point_id = state_data.get("pickup_point_id")

    default_address_obj = None
    delivery_type = None

    if not is_pickup:
        delivery_type = DeliveryType.LOCAL_SAME_DAY
        default_address_obj = (
            await session.get(DeliveryAddress, default_address_id)
            if default_address_id
            else None
        )

        if not isinstance(default_address_obj, DeliveryAddress):
            error_msg = manager.get_message("checkout", "error_address_not_found")
            await callback_message.edit_text(error_msg)
            await state.clear()
            return
    else:
        delivery_type = DeliveryType.PICKUP_STORE
        if not pickup_point_id:
            await callback_message.edit_text("⚠️ Error: No pickup point selected.")
            await state.clear()
            return

    try:
        order = await order_service.place_order(
            session=session,
            db_user=db_user,
            delivery_type=delivery_type,
            delivery_address=default_address_obj,
            pickup_point_id=pickup_point_id,
        )

        order_dto = OrderDTO.model_validate(order)

        # Notify admins
        await notification_service.notify_admins_new_order(query.bot, order_dto)

        success_msg = manager.get_message(
            "checkout",
            "success_order_placed",
            order_number=order_dto.display_order_number,
        )
        await callback_message.edit_text(success_msg)
    except OrderPlacementError as e:
        await callback_message.edit_text(f"⚠️ <b>Error:</b> {escape(str(e))}")
    except Exception as e:
        logger.error(
            f"Unexpected checkout error for user {db_user.id}: {e}", exc_info=True
        )
        error_msg = manager.get_message("checkout", "error_unexpected")
        await callback_message.edit_text(error_msg)
    finally:
        await state.clear()
        await query.answer()


@router.callback_query(
    CheckoutFSM.confirm_fast_path,
    CheckoutCallbackFactory.filter(F.action == "cancel"),  # type: ignore[arg-type]
)
async def fast_checkout_cancel_handler(
    query: CallbackQuery, state: FSMContext, callback_message: Message
):
    """Handles cancellation from the fast path confirmation."""
    cancel_msg = manager.get_message("checkout", "checkout_cancelled")
    await callback_message.edit_text(cancel_msg)
    await state.clear()
    await query.answer()


@router.callback_query(
    CheckoutFSM.confirm_fast_path,
    CheckoutCallbackFactory.filter(F.action == "edit_details"),  # type: ignore[arg-type]
)
async def fast_checkout_edit_handler(
    query: CallbackQuery,
    state: FSMContext,
    callback_message: Message,
    session: AsyncSession,
    db_user: User,
):
    """Redirects the user to their profile for editing details."""
    await state.clear()

    from ..profile import profile_handler

    # Send a new message instead of using the deleted callback message
    new_message = await callback_message.answer("Loading your profile...")
    await profile_handler(new_message, session, db_user)

    # Delete the original callback message after sending the new one
    await callback_message.delete()
    await query.answer("You can now edit your details.")
