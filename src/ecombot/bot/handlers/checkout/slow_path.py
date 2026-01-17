"""Slow path checkout handlers for first-time users."""

from html import escape

from aiogram import F
from aiogram import Router
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import CheckoutCallbackFactory
from ecombot.bot.callback_data import PickupSelectCallbackFactory
from ecombot.bot.keyboards.checkout import get_checkout_confirmation_keyboard
from ecombot.bot.keyboards.checkout import get_request_contact_keyboard
from ecombot.bot.middlewares import MessageInteractionMiddleware
from ecombot.core.manager import central_manager as manager
from ecombot.db.models import PickupPoint
from ecombot.db.models import User
from ecombot.logging_setup import logger
from ecombot.schemas.enums import DeliveryType
from ecombot.services import cart_service
from ecombot.services import notification_service
from ecombot.services import order_service
from ecombot.services import user_service
from ecombot.services.order_service import OrderPlacementError

from .states import CheckoutFSM
from .utils import check_courier_availability
from .utils import generate_slow_path_confirmation_text
from .utils import get_active_pickup_points


router = Router()
router.callback_query.middleware(MessageInteractionMiddleware())


@router.message(CheckoutFSM.getting_name, F.text)
async def get_name_handler(message: Message, state: FSMContext):
    """Slow Path Step 1: Receives name, asks for phone."""
    await state.update_data(name=message.text)
    phone_msg = manager.get_message("checkout", "slow_path_phone")
    await message.answer(
        phone_msg,
        reply_markup=get_request_contact_keyboard(),
    )
    await state.set_state(CheckoutFSM.getting_phone)


@router.message(CheckoutFSM.getting_phone, or_f(F.text, F.contact))
async def get_phone_handler(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    db_user: User,
):
    """Slow Path Step 2: Receives phone, asks for address OR confirms if pickup."""
    phone = message.contact.phone_number if message.contact else message.text

    if not phone or not phone.strip():
        error_msg = manager.get_message("checkout", "error_empty_phone")
        await message.answer(error_msg)
        return

    await state.update_data(phone=phone.strip())

    courier_available = await check_courier_availability(session)

    if courier_available:
        await state.update_data(is_pickup=False)
        address_msg = manager.get_message("checkout", "slow_path_address")
        await message.answer(
            address_msg,
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(CheckoutFSM.getting_address)
    else:
        await state.update_data(is_pickup=True)
        # Skip address step for pickup
        # Remove the 'Request Contact' keyboard
        await message.answer("✅", reply_markup=ReplyKeyboardRemove())

        pickup_points = await get_active_pickup_points(session)
        if len(pickup_points) > 1:
            builder = InlineKeyboardBuilder()
            for pp in pickup_points:
                builder.button(
                    text=pp.name,
                    callback_data=PickupSelectCallbackFactory(pickup_point_id=pp.id),
                )
            builder.adjust(1)
            await message.answer(
                manager.get_message("delivery", "select_pickup_point"),
                reply_markup=builder.as_markup(),
            )
            await state.set_state(CheckoutFSM.choosing_pickup_slow)
        elif len(pickup_points) == 1:
            pp = pickup_points[0]
            await state.update_data(
                pickup_point_id=pp.id, pickup_point_name=f"{pp.name} ({pp.address})"
            )
            user_data = await state.get_data()
            cart_data = await cart_service.get_user_cart(session, db_user.telegram_id)
            confirmation_text = generate_slow_path_confirmation_text(
                user_data, cart_data, is_pickup=True
            )
            await message.answer(
                confirmation_text,
                reply_markup=get_checkout_confirmation_keyboard(),
            )
            await state.set_state(CheckoutFSM.confirm_slow_path)
        else:
            await message.answer(
                manager.get_message("delivery", "error_no_pickup_points")
            )


@router.callback_query(
    CheckoutFSM.choosing_pickup_slow, PickupSelectCallbackFactory.filter()
)
async def slow_path_pickup_selected(
    query: CallbackQuery,
    callback_data: PickupSelectCallbackFactory,
    state: FSMContext,
    session: AsyncSession,
    db_user: User,
):
    """Handles pickup point selection in slow path."""
    pp_id = callback_data.pickup_point_id
    pickup_point = await session.get(PickupPoint, pp_id)
    if not pickup_point:
        await query.answer(
            manager.get_message("delivery", "pp_not_found"), show_alert=True
        )
        return

    await state.update_data(
        pickup_point_id=pp_id,
        pickup_point_name=f"{pickup_point.name} ({pickup_point.address})",
    )

    user_data = await state.get_data()
    cart_data = await cart_service.get_user_cart(session, db_user.telegram_id)
    confirmation_text = generate_slow_path_confirmation_text(
        user_data, cart_data, is_pickup=True
    )
    await query.message.edit_text(
        confirmation_text,
        reply_markup=get_checkout_confirmation_keyboard(),
    )
    await state.set_state(CheckoutFSM.confirm_slow_path)


@router.message(CheckoutFSM.getting_address, F.text)
async def get_address_handler(
    message: Message, session: AsyncSession, state: FSMContext, db_user: User
):
    """Slow Path Step 3: Receives address, shows final confirmation."""
    if not message.text or not message.text.strip():
        error_msg = manager.get_message("checkout", "error_empty_address")
        await message.answer(error_msg)
        return

    await state.update_data(address=message.text.strip())
    user_data = await state.get_data()
    cart_data = await cart_service.get_user_cart(session, db_user.telegram_id)

    confirmation_text = generate_slow_path_confirmation_text(
        user_data, cart_data, is_pickup=False
    )
    await message.answer(
        confirmation_text,
        reply_markup=get_checkout_confirmation_keyboard(),
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
    progress_msg = manager.get_message("checkout", "progress_saving_details")
    await callback_message.edit_text(progress_msg)
    user_data = await state.get_data()
    is_pickup = user_data.get("is_pickup", False)
    pickup_point_id = user_data.get("pickup_point_id")

    try:
        # --- Save user info for next time ---
        # 1. Update their profile (e.g., phone)
        await user_service.update_profile_details(
            session, db_user.id, {"phone": user_data["phone"]}
        )

        new_address_model = None
        delivery_type = None

        if not is_pickup:
            delivery_type = DeliveryType.LOCAL_SAME_DAY
            # 2. Add the new address and set it as default
            new_address_model = await user_service.add_new_address(
                session, db_user.id, "Default", user_data["address"]
            )
            await user_service.set_user_default_address(
                session,
                db_user.id,
                new_address_model.id,
            )
        else:
            delivery_type = DeliveryType.PICKUP_STORE
            if not pickup_point_id:
                raise OrderPlacementError("No pickup point selected.")

        refreshed_user_obj = await session.get(User, db_user.id)
        if refreshed_user_obj is None:
            raise OrderPlacementError(
                "Could not retrieve your user profile after saving."
                " Please contact support."
            )

        order_dto = await order_service.place_order(
            session=session,
            db_user=refreshed_user_obj,
            delivery_address=new_address_model,
            delivery_type=delivery_type,
            pickup_point_id=pickup_point_id,
        )

        # Notify admins
        await notification_service.notify_admins_new_order(query.bot, order_dto)

        success_msg = manager.get_message(
            "checkout",
            "success_order_placed_slow",
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
    CheckoutFSM.confirm_slow_path,
    CheckoutCallbackFactory.filter(F.action == "cancel"),  # type: ignore[arg-type]
)
async def slow_path_cancel_handler(
    query: CallbackQuery, state: FSMContext, callback_message: Message
):
    """Handles cancellation from the slow path confirmation."""
    cancel_msg = manager.get_message("checkout", "checkout_cancelled")
    await callback_message.edit_text(cancel_msg)
    await state.clear()
    await query.answer()
