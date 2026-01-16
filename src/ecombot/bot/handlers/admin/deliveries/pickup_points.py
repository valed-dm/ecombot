from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import DeliveryAdminCallbackFactory
from ecombot.bot.callback_data import PickupTypeCallbackFactory
from ecombot.core.manager import central_manager as manager
from ecombot.db.crud import deliveries as deliveries_crud
from ecombot.schemas.enums import DeliveryType

from .menu import send_delivery_menu
from .states import PickupPointStates


router = Router()


@router.callback_query(DeliveryAdminCallbackFactory.filter(F.action == "pp_list"))
async def cb_list_pickup_points(query: CallbackQuery, session: AsyncSession):
    """Lists all pickup points."""
    points = await deliveries_crud.get_all_pickup_points(session)

    builder = InlineKeyboardBuilder()
    for pp in points:
        status = "✅" if pp.is_active else "❌"
        builder.button(
            text=f"{status} {pp.name}",
            callback_data=DeliveryAdminCallbackFactory(
                action="pp_edit", item_id=pp.id
            ).pack(),
        )

    builder.button(
        text=manager.get_message("keyboards", "add_pickup_point"),
        callback_data=DeliveryAdminCallbackFactory(action="pp_add").pack(),
    )
    builder.button(
        text=manager.get_message("keyboards", "view_addresses"),
        callback_data=DeliveryAdminCallbackFactory(action="pp_view_all").pack(),
    )
    builder.button(
        text=manager.get_message("keyboards", "back"),
        callback_data=DeliveryAdminCallbackFactory(action="menu").pack(),
    )
    builder.adjust(1)

    text = manager.get_message("delivery", "pp_list_text")
    await query.message.edit_text(
        text,
        reply_markup=builder.as_markup(),
    )


@router.callback_query(DeliveryAdminCallbackFactory.filter(F.action == "pp_edit"))
async def cb_edit_pickup_point(
    query: CallbackQuery,
    callback_data: DeliveryAdminCallbackFactory,
    session: AsyncSession,
):
    """Shows details and actions for a specific pickup point."""
    pp_id = callback_data.item_id
    pp = await deliveries_crud.get_pickup_point(session, pp_id)

    if not pp:
        await query.answer(
            manager.get_message("delivery", "pp_not_found"), show_alert=True
        )
        return await cb_list_pickup_points(query, session)

    status_key = "status_active" if pp.is_active else "status_inactive"
    status_text = manager.get_message("delivery", status_key)
    type_text = manager.get_message("delivery", pp.pickup_type.message_key)

    text = manager.get_message(
        "delivery",
        "pp_details",
        name=pp.name,
        address=pp.address,
        type=type_text,
        hours=pp.working_hours or "N/A",
        status=status_text,
    )

    builder = InlineKeyboardBuilder()
    toggle_key = "disable" if pp.is_active else "enable"
    toggle_text = manager.get_message("keyboards", toggle_key)

    builder.button(
        text=toggle_text,
        callback_data=DeliveryAdminCallbackFactory(
            action="pp_toggle", item_id=pp.id
        ).pack(),
    )
    builder.button(
        text=manager.get_message("keyboards", "delete"),
        callback_data=DeliveryAdminCallbackFactory(
            action="pp_delete", item_id=pp.id
        ).pack(),
    )
    builder.button(
        text=manager.get_message("keyboards", "back"),
        callback_data=DeliveryAdminCallbackFactory(action="pp_list").pack(),
    )
    builder.adjust(1)

    await query.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(DeliveryAdminCallbackFactory.filter(F.action == "pp_toggle"))
async def cb_toggle_pickup_point(
    query: CallbackQuery,
    callback_data: DeliveryAdminCallbackFactory,
    session: AsyncSession,
):
    pp_id = callback_data.item_id
    pp = await deliveries_crud.toggle_pickup_point_status(session, pp_id)
    if pp:
        await query.answer(manager.get_message("delivery", "status_updated"))
        # Refresh view
        # We can reuse the callback_data since it has the item_id, just change action
        callback_data.action = "pp_edit"
        await cb_edit_pickup_point(query, callback_data, session)


@router.callback_query(DeliveryAdminCallbackFactory.filter(F.action == "pp_delete"))
async def cb_delete_pickup_point(
    query: CallbackQuery,
    callback_data: DeliveryAdminCallbackFactory,
    session: AsyncSession,
):
    pp_id = callback_data.item_id
    if await deliveries_crud.delete_pickup_point(session, pp_id):
        await query.answer(manager.get_message("delivery", "pp_deleted"))
    await cb_list_pickup_points(query, session)


@router.callback_query(DeliveryAdminCallbackFactory.filter(F.action == "pp_view_all"))
async def cb_view_pickup_addresses(query: CallbackQuery, session: AsyncSession):
    """Sends a message listing all pickup points and their addresses."""
    points = await deliveries_crud.get_all_pickup_points(session)

    if not points:
        await query.answer(
            manager.get_message("delivery", "no_pp_found"), show_alert=True
        )
        return

    lines = [manager.get_message("delivery", "pp_addresses_header")]
    for pp in points:
        status = "✅" if pp.is_active else "❌"
        lines.append(f"{status} <b>{pp.name}</b>\n{pp.address}\n")

    text = "\n".join(lines)
    await query.message.answer(text)
    await query.answer()


# --- Add Pickup Point FSM ---


@router.callback_query(DeliveryAdminCallbackFactory.filter(F.action == "pp_add"))
async def cb_add_pickup_start(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text(
        manager.get_message("delivery", "enter_pp_name")
    )
    await state.set_state(PickupPointStates.waiting_for_name)


@router.message(PickupPointStates.waiting_for_name)
async def process_pp_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        manager.get_message("delivery", "enter_pp_address")
    )
    await state.set_state(PickupPointStates.waiting_for_address)


@router.message(PickupPointStates.waiting_for_address)
async def process_pp_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)

    # Ask for type using buttons
    builder = InlineKeyboardBuilder()
    builder.button(
        text=manager.get_message("keyboards", "pickup_store"),
        callback_data=PickupTypeCallbackFactory(type_value="pickup_store").pack(),
    )
    builder.button(
        text=manager.get_message("keyboards", "pickup_locker"),
        callback_data=PickupTypeCallbackFactory(type_value="pickup_locker").pack(),
    )
    builder.button(
        text=manager.get_message("keyboards", "pickup_curbside"),
        callback_data=PickupTypeCallbackFactory(type_value="pickup_curbside").pack(),
    )
    builder.adjust(1)

    await message.answer(
        manager.get_message("delivery", "select_pp_type"),
        reply_markup=builder.as_markup(),
    )
    await state.set_state(PickupPointStates.waiting_for_type)


@router.callback_query(
    PickupPointStates.waiting_for_type, PickupTypeCallbackFactory.filter()
)
async def process_pp_type(
    query: CallbackQuery, callback_data: PickupTypeCallbackFactory, state: FSMContext
):
    p_type = callback_data.type_value
    # Validate enum
    try:
        enum_val = DeliveryType(p_type)
    except ValueError:
        await query.answer(manager.get_message("delivery", "invalid_type"))
        return

    await state.update_data(pickup_type=enum_val)
    type_text = manager.get_message("delivery", enum_val.message_key)
    await query.message.edit_text(
        manager.get_message("delivery", "enter_pp_hours", type=type_text)
    )
    await state.set_state(PickupPointStates.waiting_for_hours)


@router.message(PickupPointStates.waiting_for_hours)
async def process_pp_hours(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    hours = message.text

    new_pp = await deliveries_crud.create_pickup_point(
        session,
        name=data["name"],
        address=data["address"],
        pickup_type=data["pickup_type"],
        working_hours=hours,
    )

    await message.answer(
        manager.get_message("delivery", "pp_created", name=new_pp.name)
    )
    await state.clear()
    await send_delivery_menu(message)
