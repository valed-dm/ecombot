from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import DeliveryAdminCallbackFactory
from ecombot.bot.callback_data import PickupTypeCallbackFactory
from ecombot.db.models import PickupPoint
from ecombot.schemas.enums import DeliveryType

from .menu import send_delivery_menu
from .states import PickupPointStates


router = Router()


@router.callback_query(DeliveryAdminCallbackFactory.filter(F.action == "pp_list"))
async def cb_list_pickup_points(query: CallbackQuery, session: AsyncSession):
    """Lists all pickup points."""
    stmt = select(PickupPoint).order_by(PickupPoint.id)
    result = await session.execute(stmt)
    points = result.scalars().all()

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
        text="➕ Add New Pickup Point",
        callback_data=DeliveryAdminCallbackFactory(action="pp_add").pack(),
    )
    builder.button(
        text="📋 View Addresses",
        callback_data=DeliveryAdminCallbackFactory(action="pp_view_all").pack(),
    )
    builder.button(
        text="🔙 Back", callback_data=DeliveryAdminCallbackFactory(action="menu").pack()
    )
    builder.adjust(1)

    await query.message.edit_text(
        "<b>📍 Pickup Points</b>\nSelect a point to toggle availability or delete.",
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
    pp = await session.get(PickupPoint, pp_id)

    if not pp:
        await query.answer("Pickup point not found.", show_alert=True)
        return await cb_list_pickup_points(query, session)

    text = (
        f"<b>📍 {pp.name}</b>\n\n"
        f"Address: {pp.address}\n"
        f"Type: {pp.pickup_type.value}\n"
        f"Hours: {pp.working_hours or 'N/A'}\n"
        f"Status: {'Active ✅' if pp.is_active else 'Inactive ❌'}"
    )

    builder = InlineKeyboardBuilder()
    toggle_text = "Disable ❌" if pp.is_active else "Enable ✅"
    builder.button(
        text=toggle_text,
        callback_data=DeliveryAdminCallbackFactory(
            action="pp_toggle", item_id=pp.id
        ).pack(),
    )
    builder.button(
        text="🗑️ Delete",
        callback_data=DeliveryAdminCallbackFactory(
            action="pp_delete", item_id=pp.id
        ).pack(),
    )
    builder.button(
        text="🔙 Back",
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
    pp = await session.get(PickupPoint, pp_id)
    if pp:
        pp.is_active = not pp.is_active
        await session.commit()
        await query.answer("Status updated.")
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
    pp = await session.get(PickupPoint, pp_id)
    if pp:
        await session.delete(pp)
        await session.commit()
        await query.answer("Pickup point deleted.")
    await cb_list_pickup_points(query, session)


@router.callback_query(DeliveryAdminCallbackFactory.filter(F.action == "pp_view_all"))
async def cb_view_pickup_addresses(query: CallbackQuery, session: AsyncSession):
    """Sends a message listing all pickup points and their addresses."""
    stmt = select(PickupPoint).order_by(PickupPoint.id)
    result = await session.execute(stmt)
    points = result.scalars().all()

    if not points:
        await query.answer("No pickup points found.", show_alert=True)
        return

    lines = ["<b>📍 Pickup Point Addresses:</b>\n"]
    for pp in points:
        status = "✅" if pp.is_active else "❌"
        lines.append(f"{status} <b>{pp.name}</b>\n{pp.address}\n")

    text = "\n".join(lines)
    await query.message.answer(text)
    await query.answer()


# --- Add Pickup Point FSM ---


@router.callback_query(DeliveryAdminCallbackFactory.filter(F.action == "pp_add"))
async def cb_add_pickup_start(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text("Enter the <b>Name</b> for the new pickup point:")
    await state.set_state(PickupPointStates.waiting_for_name)


@router.message(PickupPointStates.waiting_for_name)
async def process_pp_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Enter the <b>Full Address</b>:")
    await state.set_state(PickupPointStates.waiting_for_address)


@router.message(PickupPointStates.waiting_for_address)
async def process_pp_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)

    # Ask for type using buttons
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Store",
        callback_data=PickupTypeCallbackFactory(type_value="pickup_store").pack(),
    )
    builder.button(
        text="Locker",
        callback_data=PickupTypeCallbackFactory(type_value="pickup_locker").pack(),
    )
    builder.button(
        text="Curbside",
        callback_data=PickupTypeCallbackFactory(type_value="pickup_curbside").pack(),
    )
    builder.adjust(1)

    await message.answer(
        "Select the <b>Pickup Type</b>:", reply_markup=builder.as_markup()
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
        await query.answer("Invalid type.")
        return

    await state.update_data(pickup_type=enum_val)
    await query.message.edit_text(
        f"Selected: {enum_val.value}\n\n"
        "Enter <b>Working Hours</b> (e.g., 'Mon-Fri 9-18'):"
    )
    await state.set_state(PickupPointStates.waiting_for_hours)


@router.message(PickupPointStates.waiting_for_hours)
async def process_pp_hours(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    hours = message.text

    new_pp = PickupPoint(
        name=data["name"],
        address=data["address"],
        pickup_type=data["pickup_type"],
        working_hours=hours,
        is_active=True,
    )
    session.add(new_pp)
    await session.commit()

    await message.answer(f"✅ Pickup point <b>{new_pp.name}</b> created successfully!")
    await state.clear()
    await send_delivery_menu(message)
