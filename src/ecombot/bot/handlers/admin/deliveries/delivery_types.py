from aiogram import F
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import DeliveryAdminCallbackFactory
from ecombot.core.manager import central_manager as manager
from ecombot.db.crud import deliveries as deliveries_crud
from ecombot.schemas.enums import DeliveryType


router = Router()


@router.callback_query(DeliveryAdminCallbackFactory.filter(F.action == "dt_list"))
async def cb_list_delivery_types(query: CallbackQuery, session: AsyncSession):
    """Lists all available delivery types and their status."""
    # Fetch existing configured options
    options = await deliveries_crud.get_all_delivery_options(session)
    existing_options = {opt.delivery_type: opt for opt in options}

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

        # Label formatting using i18n
        label = manager.get_message("delivery", dt.message_key)
        builder.button(
            text=f"{status_icon} {label}",
            callback_data=DeliveryAdminCallbackFactory(
                action="dt_toggle", value=dt.value
            ).pack(),
        )

    builder.button(
        text=manager.get_message("keyboards", "back"),
        callback_data=DeliveryAdminCallbackFactory(action="menu").pack(),
    )
    builder.adjust(1)

    await query.message.edit_text(
        manager.get_message("delivery", "dt_list_text"),
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
        await query.answer(manager.get_message("delivery", "invalid_dt"))
        return

    option = await deliveries_crud.toggle_delivery_option(session, dt_enum)
    status_key = "active" if option.is_active else "inactive"
    status_text = manager.get_message("delivery", status_key)
    type_text = manager.get_message("delivery", dt_enum.message_key)

    await query.answer(
        manager.get_message("delivery", "dt_toggled", type=type_text, status=status_text)
    )
    await cb_list_delivery_types(query, session)
