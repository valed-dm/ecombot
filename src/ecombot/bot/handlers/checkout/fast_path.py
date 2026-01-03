"""Fast path checkout handlers for returning users."""

from html import escape

from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import CheckoutCallbackFactory
from ecombot.bot.middlewares import MessageInteractionMiddleware
from ecombot.db.models import DeliveryAddress
from ecombot.db.models import User
from ecombot.logging_setup import logger
from ecombot.services import order_service
from ecombot.services.order_service import OrderPlacementError

from .states import CHECKOUT_CANCELLED
from .states import ERROR_ADDRESS_NOT_FOUND
from .states import ERROR_UNEXPECTED
from .states import PROGRESS_PLACING_ORDER
from .states import SUCCESS_ORDER_PLACED
from .states import CheckoutFSM


router = Router()
router.callback_query.middleware(MessageInteractionMiddleware())


@router.callback_query(
    CheckoutFSM.confirm_fast_path, CheckoutCallbackFactory.filter(F.action == "confirm")  # type: ignore[arg-type]
)
async def fast_checkout_confirm_handler(
    query: CallbackQuery,
    session: AsyncSession,
    db_user: User,
    state: FSMContext,
    callback_message: Message,
):
    """Handles the final confirmation for the fast path checkout."""
    await callback_message.edit_text(PROGRESS_PLACING_ORDER)

    state_data = await state.get_data()
    default_address_id = state_data.get("default_address_id")

    default_address_obj = (
        await session.get(DeliveryAddress, default_address_id)
        if default_address_id
        else None
    )

    if not isinstance(default_address_obj, DeliveryAddress):
        await callback_message.edit_text(ERROR_ADDRESS_NOT_FOUND)
        await state.clear()
        return

    try:
        order = await order_service.place_order(
            session=session, db_user=db_user, delivery_address=default_address_obj
        )
        success_text = SUCCESS_ORDER_PLACED.format(order_number=order.order_number)
        await callback_message.edit_text(success_text)
    except OrderPlacementError as e:
        await callback_message.edit_text(f"⚠️ <b>Error:</b> {escape(str(e))}")
    except Exception as e:
        logger.error(
            f"Unexpected checkout error for user {db_user.id}: {e}", exc_info=True
        )
        await callback_message.edit_text(ERROR_UNEXPECTED)
    finally:
        await state.clear()
        await query.answer()


@router.callback_query(
    CheckoutFSM.confirm_fast_path, CheckoutCallbackFactory.filter(F.action == "cancel")  # type: ignore[arg-type]
)
async def fast_checkout_cancel_handler(
    query: CallbackQuery, state: FSMContext, callback_message: Message
):
    """Handles cancellation from the fast path confirmation."""
    await callback_message.edit_text(CHECKOUT_CANCELLED)
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
