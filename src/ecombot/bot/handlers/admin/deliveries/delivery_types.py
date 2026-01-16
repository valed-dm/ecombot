from aiogram import F
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import DeliveryAdminCallbackFactory
from ecombot.db.models import DeliveryOption
from ecombot.schemas.enums import DeliveryType


router = Router()


@router.callback_query(DeliveryAdminCallbackFactory.filter(F.action == "dt_list"))
async def cb_list_delivery_types(query: CallbackQuery, session: AsyncSession):
    """Lists all available delivery types and their status."""
    # Fetch existing configured options
    stmt = select(DeliveryOption)
    result = await session.execute(stmt)
    existing_options = {opt.delivery_type: opt for opt in result.scalars().all()}

    builder = InlineKeyboardBuilder()

    # Iterate over all defined DeliveryType enums
    for dt in DeliveryType:
        # Skip pickup types here as they are managed via Pickup Points usually,
        # but we can allow enabling them if they have fees.
        # For clarity, let's list all.

        opt = existing_options.get(dt)
        is_active = opt.is_active if opt else False
        status_icon = (
            "✅" if is_active else "⚪"
        )  # White circle for unconfigured/inactive

        # Label formatting
        label = dt.value.replace("_", " ").title()
        builder.button(
            text=f"{status_icon} {label}",
            callback_data=DeliveryAdminCallbackFactory(
                action="dt_toggle", value=dt.value
            ).pack(),
        )

    builder.button(
        text="🔙 Back", callback_data=DeliveryAdminCallbackFactory(action="menu").pack()
    )
    builder.adjust(1)

    await query.message.edit_text(
        "<b>🚚 Delivery Types</b>\n"
        "Tap to toggle availability.\n"
        "⚪ = Inactive/Not Configured\n"
        "✅ = Active",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(DeliveryAdminCallbackFactory.filter(F.action == "dt_toggle"))
async def cb_toggle_delivery_type(
    query: CallbackQuery,
    callback_data: DeliveryAdminCallbackFactory,
    session: AsyncSession,
):
    dt_value = callback_data.value
    try:
        dt_enum = DeliveryType(dt_value)
    except ValueError:
        await query.answer("Invalid delivery type.")
        return

    # Check if option exists
    stmt = select(DeliveryOption).where(DeliveryOption.delivery_type == dt_enum)
    result = await session.execute(stmt)
    option = result.scalar_one_or_none()

    if option:
        # Toggle existing
        option.is_active = not option.is_active
        status = "Active" if option.is_active else "Inactive"
        await query.answer(f"{dt_enum.value} is now {status}")
    else:
        # Create new default option (Active)
        # Defaulting price to 0. Admin can edit price later (feature to be added)
        new_option = DeliveryOption(
            delivery_type=dt_enum,
            name=dt_enum.value.replace("_", " ").title(),
            price=0,
            is_active=True,
        )
        session.add(new_option)
        await query.answer(f"{dt_enum.value} activated (Price: 0)")

    await session.commit()
    await cb_list_delivery_types(query, session)
