"""Order viewing and filtering handlers."""

from aiogram import F
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from ecombot.bot.callback_data import AdminCallbackFactory
from ecombot.bot.callback_data import OrderCallbackFactory
from ecombot.bot.keyboards.admin import get_admin_order_filters_keyboard
from ecombot.bot.keyboards.admin import get_admin_orders_list_keyboard
from ecombot.db import crud
from ecombot.schemas.dto import OrderDTO
from ecombot.schemas.enums import OrderStatus
from ecombot.services import order_service

from .constants import ERROR_ORDER_NOT_FOUND
from .constants import ERROR_QUERY_DATA_NONE
from .constants import NO_ORDERS_FOUND
from .constants import ORDERS_LIST_HEADER
from .constants import PROGRESS_FETCHING_ORDERS
from .constants import SELECT_STATUS_PROMPT
from .utils import InvalidQueryDataError
from .utils import send_order_details_view


router = Router()


@router.callback_query(AdminCallbackFactory.filter(F.action == "view_orders"))  # type: ignore[arg-type]
async def view_orders_start_handler(query: CallbackQuery, callback_message: Message):
    """Entry point for viewing orders. Displays the status filter keyboard."""
    keyboard = get_admin_order_filters_keyboard()
    await callback_message.edit_text(SELECT_STATUS_PROMPT, reply_markup=keyboard)
    await query.answer()


@router.callback_query(F.data.startswith("admin_order_filter:"))
async def filter_orders_by_status_handler(
    query: CallbackQuery, session: AsyncSession, callback_message: Message
):
    """Handle status filter button clicks. Fetch and display orders by status."""
    if query.data is None:
        raise InvalidQueryDataError(ERROR_QUERY_DATA_NONE)

    status_value = query.data.split(":")[1]
    status = OrderStatus(status_value)

    await callback_message.edit_text(
        PROGRESS_FETCHING_ORDERS.format(status=status.name.lower())
    )

    orders = await order_service.get_orders_by_status_for_admin(session, status)

    text = ORDERS_LIST_HEADER.format(status=status.name.capitalize(), count=len(orders))
    if not orders:
        text += NO_ORDERS_FOUND

    keyboard = get_admin_orders_list_keyboard(orders)
    await callback_message.edit_text(text, reply_markup=keyboard)
    await query.answer()


@router.callback_query(OrderCallbackFactory.filter(F.action == "view_details"))  # type: ignore[arg-type]
async def admin_view_order_details_handler(
    query: CallbackQuery,
    callback_data: OrderCallbackFactory,
    session: AsyncSession,
    callback_message: Message,
):
    """Display detailed view of a specific order for an admin."""
    order = None
    order_id = callback_data.item_id
    if order_id is not None:
        order = await crud.get_order(session, order_id)

    if not order:
        await query.answer(ERROR_ORDER_NOT_FOUND, show_alert=True)
        return

    order_dto = OrderDTO.model_validate(order)
    await send_order_details_view(callback_message, order_dto)
    await query.answer()
