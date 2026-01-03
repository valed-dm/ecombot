"""Order status management handlers."""

from aiogram import Bot
from aiogram import F
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.db import crud
from ecombot.logging_setup import log
from ecombot.schemas.dto import OrderDTO
from ecombot.schemas.enums import OrderStatus
from ecombot.services import notification_service
from ecombot.services import order_service

from .constants import ERROR_INVALID_ORDER_ID
from .constants import ERROR_QUERY_DATA_NONE
from .constants import ERROR_STATUS_UPDATE_FAILED
from .constants import SUCCESS_STATUS_UPDATED
from .utils import InvalidQueryDataError
from .utils import send_order_details_view


router = Router()


@router.callback_query(F.data.startswith("admin_order_status:"))
async def change_order_status_handler(
    query: CallbackQuery,
    session: AsyncSession,
    callback_message: Message,
    bot: Bot,
):
    """Handle order status change button clicks."""
    if query.data is None:
        raise InvalidQueryDataError(ERROR_QUERY_DATA_NONE)

    _, order_id_str, new_status_value = query.data.split(":")

    try:
        order_id = int(order_id_str)
    except ValueError:
        await query.answer(ERROR_INVALID_ORDER_ID, show_alert=True)
        return

    new_status = OrderStatus(new_status_value)

    try:
        updated_order_dto = await order_service.change_order_status(
            session, order_id, new_status
        )
        await query.answer(
            SUCCESS_STATUS_UPDATED.format(status=new_status.name.capitalize()),
            show_alert=True,
        )
        await notification_service.send_order_status_update(bot, updated_order_dto)

        # Refresh the admin's detailed view
        await send_order_details_view(callback_message, updated_order_dto)

    except Exception as e:
        log.error(f"Failed to change status for order {order_id}: {e}", exc_info=True)
        await query.answer(ERROR_STATUS_UPDATE_FAILED, show_alert=True)
        await _attempt_refresh_order_view(session, callback_message, order_id)


async def _attempt_refresh_order_view(
    session: AsyncSession, message: Message, order_id: int
):
    """Attempt to refresh the order view even if status update failed."""
    try:
        order = await crud.get_order(session, order_id)
        if order:
            order_dto = OrderDTO.model_validate(order)
            await send_order_details_view(message, order_dto)
    except Exception as refresh_e:
        log.error(f"Failed to refresh order view for order {order_id}: {refresh_e}")
