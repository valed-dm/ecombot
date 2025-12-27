"""
Handlers for the new, smarter checkout process.

This module contains the FSM and handlers to guide the user through
collecting their contact information and confirming their order. It features
a "fast path" for returning users with complete profiles and a "slow path"
for first-time users, which then saves their details for future use.
"""

from html import escape

from aiogram import F
from aiogram import Router
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot import keyboards
from ecombot.bot.callback_data import CheckoutCallbackFactory
from ecombot.bot.middlewares import MessageInteractionMiddleware
from ecombot.db.models import DeliveryAddress
from ecombot.db.models import User
from ecombot.logging_setup import logger
from ecombot.services import cart_service
from ecombot.services import order_service
from ecombot.services import user_service
from ecombot.services.order_service import OrderPlacementError


# =============================================================================
# Router and Middleware Setup
# =============================================================================


router = Router()
router.callback_query.middleware(MessageInteractionMiddleware())


# =============================================================================
# FSM Definition
# =============================================================================


class CheckoutFSM(StatesGroup):
    # States for the "slow path" / first-time user
    getting_name = State()
    getting_phone = State()
    getting_address = State()
    confirm_slow_path = State()

    # State for the "fast path" / returning user
    confirm_fast_path = State()


# =============================================================================
# Checkout Flow Start
# =============================================================================


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
        await callback_message.answer("Your cart is empty.")
        return

    default_address = next(
        (addr for addr in db_user.addresses if addr.is_default), None
    )

    if db_user.phone and default_address:
        # --- FAST PATH ---
        await state.update_data(default_address_id=default_address.id)
        confirmation_text = (
            "<b>Confirm Your Order</b>\n\n"
            "Your order will be shipped to your default address:\n"
            f"<code>{escape(default_address.full_address or '')}</code>\n\n"
            f"Contact Phone: <code>{escape(db_user.phone or 'Not set')}</code>\n"
            f"<b>Total Price: ${cart.total_price:.2f}</b>"
        )
        keyboard = keyboards.get_fast_checkout_confirmation_keyboard()
        await callback_message.answer(confirmation_text, reply_markup=keyboard)
        await state.set_state(CheckoutFSM.confirm_fast_path)
    else:
        # --- SLOW PATH ---
        missing_info = []
        if not db_user.phone:
            missing_info.append("phone number")
        if not default_address:
            missing_info.append("default address")
        await callback_message.answer(
            f"To complete your order, we need to set up your"
            f" {', '.join(missing_info)}.\n\n"
            "Let's start with your full name (as it should appear on the package)."
        )
        await state.set_state(CheckoutFSM.getting_name)


# =============================================================================
# Fast Path Handlers
# =============================================================================


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
    await callback_message.edit_text("Placing your order, please wait...")

    state_data = await state.get_data()
    default_address_id = state_data.get("default_address_id")

    default_address_obj = (
        await session.get(DeliveryAddress, default_address_id)
        if default_address_id
        else None
    )

    if not isinstance(default_address_obj, DeliveryAddress):
        await callback_message.edit_text(
            "Error: Could not find your default address."
            " Please try again or update your profile."
        )
        await state.clear()
        return

    try:
        order = await order_service.place_order(
            session=session, db_user=db_user, delivery_address=default_address_obj
        )
        success_text = (
            f"✅ <b>Thank you! Your order #{order.order_number}"
            f" has been placed!</b>"
        )
        await callback_message.edit_text(success_text)
    except OrderPlacementError as e:
        await callback_message.edit_text(f"⚠️ <b>Error:</b> {escape(str(e))}")
    except Exception as e:
        logger.error(
            f"Unexpected checkout error for user {db_user.id}: {e}", exc_info=True
        )
        await callback_message.edit_text(
            "An unexpected error occurred. Please contact support."
        )
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
    await callback_message.edit_text("Checkout cancelled.")
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

    from .profile import profile_handler

    # Send a new message instead of using the deleted callback message
    new_message = await callback_message.answer("Loading your profile...")
    await profile_handler(new_message, session, db_user)

    # Delete the original callback message after sending the new one
    await callback_message.delete()
    await query.answer("You can now edit your details.")


# =============================================================================
# Slow Path Handlers (First-Time Checkout)
# =============================================================================


@router.message(CheckoutFSM.getting_name, F.text)
async def get_name_handler(message: Message, state: FSMContext):
    """Slow Path Step 1: Receives name, asks for phone."""
    await state.update_data(name=message.text)
    await message.answer(
        "Thank you. Now, please share your phone number.",
        reply_markup=keyboards.get_request_contact_keyboard(),
    )
    await state.set_state(CheckoutFSM.getting_phone)


@router.message(CheckoutFSM.getting_phone, or_f(F.text, F.contact))
async def get_phone_handler(message: Message, state: FSMContext):
    """Slow Path Step 2: Receives phone, asks for address."""
    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone=phone)
    await message.answer(
        "Great. Finally, what is the full shipping address?",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(CheckoutFSM.getting_address)


@router.message(CheckoutFSM.getting_address, F.text)
async def get_address_handler(
    message: Message, session: AsyncSession, state: FSMContext, db_user: User
):
    """Slow Path Step 3: Receives address, shows final confirmation."""
    if not message.text or not message.text.strip():
        await message.answer("Please enter a valid shipping address (cannot be empty).")
        return

    await state.update_data(address=message.text.strip())
    user_data = await state.get_data()
    cart_data = await cart_service.get_user_cart(session, db_user.telegram_id)

    confirmation_text = (
        "<b>Please confirm your details:</b>\n\n"
        f"<b>Contact:</b> {escape(user_data['name'])}, {escape(user_data['phone'])}\n"
        f"<b>Shipping to:</b>\n<code>{escape(user_data['address'])}</code>\n\n"
        f"<b>Total Price: ${cart_data.total_price:.2f}</b>"
    )
    await message.answer(
        confirmation_text,
        reply_markup=keyboards.get_checkout_confirmation_keyboard(),
    )
    await state.set_state(CheckoutFSM.confirm_slow_path)


@router.callback_query(
    CheckoutFSM.confirm_slow_path,
    CheckoutCallbackFactory.filter(F.action == "confirm"),  # type: ignore[arg-type]
)
async def slow_path_confirm_handler(
    query: CallbackQuery,
    session: AsyncSession,
    db_user: User,
    state: FSMContext,
    callback_message: Message,
):
    """Slow Path Step 4: Confirmed. Places order AND saves user info."""
    await callback_message.edit_text("Placing your order and saving your details...")
    user_data = await state.get_data()

    try:
        async with session.begin():
            # --- Save user info for next time ---
            # 1. Update their profile (e.g., phone)
            await user_service.update_profile_details(
                session, db_user.id, {"phone": user_data["phone"]}
            )
            # 2. Add the new address and set it as default
            new_address_model = await user_service.add_new_address(
                session, db_user.id, "Default", user_data["address"]
            )
            await user_service.set_user_default_address(
                session,
                db_user.id,
                new_address_model.id,
            )

            refreshed_user_obj = await session.get(User, db_user.id)
            if not isinstance(refreshed_user_obj, User):
                raise OrderPlacementError(
                    "Could not retrieve your user profile after saving."
                    " Please contact support."
                )

            order = await order_service.place_order(
                session=session,
                db_user=refreshed_user_obj,
                delivery_address=new_address_model,
            )

        success_text = (
            f"✅ <b>Thank you! Your order has been placed successfully!</b>\n\n"
            f"<b>Order Number:</b> <code>{order.order_number}</code>\n"
            f"You can view its status in /orders."
        )
        await callback_message.edit_text(success_text)

    except OrderPlacementError as e:
        await callback_message.edit_text(f"⚠️ <b>Error:</b> {escape(str(e))}")
    except Exception as e:
        logger.error(
            f"Unexpected checkout error for user {db_user.id}: {e}", exc_info=True
        )
        await callback_message.edit_text(
            "An unexpected error occurred. Please contact support."
        )
    finally:
        await state.clear()
        await query.answer()


@router.callback_query(
    CheckoutFSM.confirm_slow_path, CheckoutCallbackFactory.filter(F.action == "cancel")  # type: ignore[arg-type]
)
async def slow_path_cancel_handler(
    query: CallbackQuery, state: FSMContext, callback_message: Message
):
    """Handles cancellation from the slow path confirmation."""
    await callback_message.edit_text("Checkout cancelled.")
    await state.clear()
    await query.answer()
